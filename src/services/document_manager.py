"""
Document Management Service

This module provides document management capabilities including upload, storage,
activation/deactivation, and integration with Elasticsearch for RAG.

Author: Adryan R A
"""

import logging
import uuid
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

# File processing imports
import pandas as pd
from langchain_core.documents import Document

from ..core.config import settings
from ..utils.document_processor import DocumentProcessor
from ..services.search_engine import SearchEngine

logger = logging.getLogger(__name__)


class DocumentManagerError(Exception):
    """Custom exception for document management errors."""
    pass


class DocumentManager:
    """
    Document management service for handling user uploads and document lifecycle.
    
    This service manages document uploads, processing, storage in Elasticsearch,
    and activation/deactivation for RAG queries.
    """
    
    def __init__(self, search_engine: SearchEngine):
        """
        Initialize the document manager.
        
        Args:
            search_engine (SearchEngine): Search engine instance for document storage
        """
        self.search_engine = search_engine
        self.processor = DocumentProcessor()
        
        # Document storage paths
        self.storage_path = Path("data/user_documents")
        self.metadata_file = self.storage_path / "documents_metadata.json"
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing document metadata
        self.documents_metadata = self._load_metadata()
        
        # Supported file types
        self.supported_types = {
            '.txt': self._process_text_file,
            '.csv': self._process_csv_file,
            '.xlsx': self._process_excel_file,
            '.pdf': self._process_pdf_file
        }
    
    def upload_document(
        self, 
        file_content: bytes, 
        filename: str, 
        category: str = "user_documents",
        activate: bool = True
    ) -> Dict[str, Any]:
        """
        Upload and process a document.
        
        Args:
            file_content (bytes): Raw file content
            filename (str): Original filename
            category (str): Document category
            activate (bool): Whether to activate for RAG queries
            
        Returns:
            Dict[str, Any]: Upload result with document information
            
        Raises:
            DocumentManagerError: If upload or processing fails
        """
        try:
            logger.info(f"Starting document upload: {filename}")
            
            # Validate file type
            file_extension = Path(filename).suffix.lower()
            if file_extension not in self.supported_types:
                raise DocumentManagerError(f"Unsupported file type: {file_extension}")
            
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Check for duplicate documents
            existing_doc = self._find_duplicate_document(file_hash, filename)
            if existing_doc:
                logger.warning(f"Duplicate document detected: {filename}")
                return {
                    "status": "duplicate",
                    "message": f"Document already exists: {existing_doc['filename']}",
                    "document": existing_doc
                }
            
            # Save file to storage
            file_path = self.storage_path / f"{document_id}_{filename}"
            file_path.write_bytes(file_content)
            
            # Process document content
            text_content = self.supported_types[file_extension](file_path)
            
            # Create document chunks
            chunks = self.processor.split_document(
                text_content,
                metadata={
                    "document_id": document_id,
                    "filename": filename,
                    "category": category,
                    "file_type": file_extension[1:],  # Remove the dot
                    "upload_date": datetime.now().isoformat(),
                    "file_hash": file_hash
                }
            )
            
            if not chunks:
                raise DocumentManagerError("No processable content found in document")
            
            # Create document metadata
            document_info = {
                "document_id": document_id,
                "filename": filename,
                "category": category,
                "file_type": file_extension[1:],
                "upload_date": datetime.now().isoformat(),
                "chunks_count": len(chunks),
                "is_active": activate,
                "file_size": len(file_content),
                "file_path": str(file_path),
                "file_hash": file_hash
            }
            
            # Store in Elasticsearch if activated
            if activate:
                self._store_chunks_in_elasticsearch(chunks, category)
                logger.info(f"Stored {len(chunks)} chunks in Elasticsearch")
            
            # Save metadata
            self.documents_metadata[document_id] = document_info
            self._save_metadata()
            
            logger.info(f"Document uploaded successfully: {document_id}")
            
            return {
                "status": "success",
                "message": f"Document uploaded successfully. Created {len(chunks)} chunks.",
                "document": document_info,
                "preview": text_content[:500] + "..." if len(text_content) > 500 else text_content
            }
            
        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            # Cleanup on failure
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            raise DocumentManagerError(f"Document upload failed: {e}")
    
    def list_documents(self) -> Dict[str, Any]:
        """
        List all documents in the system.
        
        Returns:
            Dict[str, Any]: List of documents with statistics
        """
        documents = list(self.documents_metadata.values())
        active_count = sum(1 for doc in documents if doc.get("is_active", False))
        
        return {
            "documents": documents,
            "total_count": len(documents),
            "active_count": active_count
        }
    
    def update_document_status(self, document_id: str, is_active: bool) -> Dict[str, Any]:
        """
        Update document activation status.
        
        Args:
            document_id (str): Document ID to update
            is_active (bool): New activation status
            
        Returns:
            Dict[str, Any]: Update result
            
        Raises:
            DocumentManagerError: If document not found or update fails
        """
        try:
            if document_id not in self.documents_metadata:
                raise DocumentManagerError(f"Document not found: {document_id}")
            
            document_info = self.documents_metadata[document_id]
            old_status = document_info.get("is_active", False)
            
            if old_status == is_active:
                return {
                    "status": "no_change",
                    "message": f"Document is already {'active' if is_active else 'inactive'}",
                    "document": document_info
                }
            
            # Update status
            document_info["is_active"] = is_active
            document_info["last_modified"] = datetime.now().isoformat()
            
            # Update Elasticsearch storage
            if is_active and not old_status:
                # Activate: re-process and store in Elasticsearch
                self._reactivate_document(document_info)
                logger.info(f"Activated document: {document_id}")
            elif not is_active and old_status:
                # Deactivate: remove from Elasticsearch (if needed)
                # For now, we keep documents in ES but mark them inactive in metadata
                logger.info(f"Deactivated document: {document_id}")
            
            # Save metadata
            self._save_metadata()
            
            status_text = "activated" if is_active else "deactivated"
            return {
                "status": "success",
                "message": f"Document {status_text} successfully",
                "document": document_info
            }
            
        except Exception as e:
            logger.error(f"Failed to update document status: {e}")
            raise DocumentManagerError(f"Status update failed: {e}")
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document from the system.
        
        Args:
            document_id (str): Document ID to delete
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        try:
            if document_id not in self.documents_metadata:
                raise DocumentManagerError(f"Document not found: {document_id}")
            
            document_info = self.documents_metadata[document_id]
            
            # Remove file from storage
            file_path = Path(document_info["file_path"])
            if file_path.exists():
                file_path.unlink()
            
            # Remove from metadata
            del self.documents_metadata[document_id]
            self._save_metadata()
            
            logger.info(f"Document deleted: {document_id}")
            
            return {
                "status": "success",
                "message": "Document deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise DocumentManagerError(f"Document deletion failed: {e}")
    
    def get_active_documents(self) -> List[str]:
        """
        Get list of active document IDs for RAG queries.
        
        Returns:
            List[str]: List of active document IDs
        """
        return [
            doc_id for doc_id, doc_info in self.documents_metadata.items()
            if doc_info.get("is_active", False)
        ]
    
    def _process_text_file(self, file_path: Path) -> str:
        """Process text file and extract content."""
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return file_path.read_text(encoding='latin-1')
    
    def _process_csv_file(self, file_path: Path) -> str:
        """Process CSV file and extract content."""
        try:
            df = pd.read_csv(file_path)
            # Convert DataFrame to readable text format
            text_content = f"CSV File: {file_path.name}\n\n"
            text_content += f"Columns: {', '.join(df.columns.tolist())}\n\n"
            text_content += "Data:\n"
            text_content += df.to_string(index=False)
            return text_content
        except Exception as e:
            raise DocumentManagerError(f"Failed to process CSV file: {e}")
    
    def _process_excel_file(self, file_path: Path) -> str:
        """Process Excel file and extract content."""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            text_content = f"Excel File: {file_path.name}\n\n"
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                text_content += f"Sheet: {sheet_name}\n"
                text_content += f"Columns: {', '.join(df.columns.tolist())}\n"
                text_content += "Data:\n"
                text_content += df.to_string(index=False)
                text_content += "\n\n"
            
            return text_content
        except Exception as e:
            raise DocumentManagerError(f"Failed to process Excel file: {e}")
    
    def _process_pdf_file(self, file_path: Path) -> str:
        """Process PDF file and extract content."""
        try:
            # For now, return a placeholder - you can integrate a PDF library like PyPDF2
            return f"PDF File: {file_path.name}\n\nPDF processing not yet implemented. Please convert to text format."
        except Exception as e:
            raise DocumentManagerError(f"Failed to process PDF file: {e}")
    
    def _store_chunks_in_elasticsearch(self, chunks: List[Document], category: str) -> None:
        """Store document chunks in Elasticsearch."""
        try:
            # Get or create document store for user documents
            store = self.search_engine.get_store(f"{category}_store")
            
            # Add documents to store
            store.add_documents(chunks)
            
        except Exception as e:
            logger.error(f"Failed to store chunks in Elasticsearch: {e}")
            raise DocumentManagerError(f"Elasticsearch storage failed: {e}")
    
    def _reactivate_document(self, document_info: Dict[str, Any]) -> None:
        """Reactivate a document by re-processing and storing in Elasticsearch."""
        try:
            file_path = Path(document_info["file_path"])
            if not file_path.exists():
                raise DocumentManagerError("Document file not found")
            
            # Re-process document
            file_extension = f".{document_info['file_type']}"
            text_content = self.supported_types[file_extension](file_path)
            
            # Create chunks
            chunks = self.processor.split_document(
                text_content,
                metadata={
                    "document_id": document_info["document_id"],
                    "filename": document_info["filename"],
                    "category": document_info["category"],
                    "file_type": document_info["file_type"],
                    "upload_date": document_info["upload_date"],
                    "reactivated_date": datetime.now().isoformat()
                }
            )
            
            # Store in Elasticsearch
            self._store_chunks_in_elasticsearch(chunks, document_info["category"])
            
        except Exception as e:
            logger.error(f"Failed to reactivate document: {e}")
            raise DocumentManagerError(f"Document reactivation failed: {e}")
    
    def _find_duplicate_document(self, file_hash: str, filename: str) -> Optional[Dict[str, Any]]:
        """Find duplicate document by hash or filename."""
        for doc_info in self.documents_metadata.values():
            if (doc_info.get("file_hash") == file_hash or 
                doc_info.get("filename") == filename):
                return doc_info
        return None
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load document metadata from file."""
        try:
            if self.metadata_file.exists():
                return json.loads(self.metadata_file.read_text())
        except Exception as e:
            logger.warning(f"Failed to load metadata: {e}")
        return {}
    
    def _save_metadata(self) -> None:
        """Save document metadata to file."""
        try:
            self.metadata_file.write_text(
                json.dumps(self.documents_metadata, indent=2)
            )
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            raise DocumentManagerError(f"Metadata save failed: {e}")
