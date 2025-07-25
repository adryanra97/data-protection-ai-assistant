"""
Document Ingestion Service

This module handles the ingestion of legal documents into the search engine,
including document loading, chunking, and indexing.

Author: Adryan R A
"""

import os
import glob
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

from .search_engine import SearchEngine, SearchEngineError
from ..utils.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """Custom exception for document ingestion errors."""
    pass


class DocumentIngestor:
    """
    Service for ingesting legal documents into the search engine.
    
    This class handles loading documents from various sources, processing them
    into chunks, and indexing them in Elasticsearch stores.
    """
    
    def __init__(self, search_engine: SearchEngine):
        """
        Initialize the document ingestor.
        
        Args:
            search_engine (SearchEngine): Configured search engine instance
        """
        self.search_engine = search_engine
        self.document_processor = DocumentProcessor()
        self.ingestion_stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "failed_documents": 0,
            "processed_by_category": {}
        }
    
    def ingest_all_documents(self, stores: Dict[str, any]) -> Dict[str, int]:
        """
        Ingest all documents from predefined data directories.
        
        Args:
            stores (Dict[str, any]): Dictionary mapping category names to store instances
            
        Returns:
            Dict[str, int]: Ingestion statistics
            
        Raises:
            IngestionError: If ingestion fails for critical categories
        """
        logger.info("Starting document ingestion process")
        
        # Define document categories and their data directories
        document_categories = {
            "gdpr": ("data/gdpr/", stores.get('gdpr')),
            "pdp": ("data/uupdp/", stores.get('pdp')), 
            "company": ("data/company/", stores.get('company'))
        }
        
        for category, (folder_path, store) in document_categories.items():
            if not store:
                logger.warning(f"No store provided for category: {category}")
                continue
                
            try:
                stats = self._ingest_category(category, folder_path, store)
                self.ingestion_stats["processed_by_category"][category] = stats
                logger.info(f"Completed ingestion for {category}: {stats} documents processed")
                
            except Exception as e:
                logger.error(f"Failed to ingest documents for category {category}: {e}")
                self.ingestion_stats["failed_documents"] += 1
                
                # Consider GDPR and PDP as critical categories
                if category in ["gdpr", "pdp"]:
                    raise IngestionError(f"Critical category {category} ingestion failed: {e}")
        
        logger.info(f"Document ingestion completed. Stats: {self.ingestion_stats}")
        return self.ingestion_stats
    
    def _ingest_category(self, category: str, folder_path: str, store) -> int:
        """
        Ingest documents for a specific category.
        
        Args:
            category (str): Document category name
            folder_path (str): Path to the folder containing documents
            store: Elasticsearch store for this category
            
        Returns:
            int: Number of documents successfully processed
            
        Raises:
            IngestionError: If folder doesn't exist or no documents found
        """
        if not os.path.exists(folder_path):
            logger.warning(f"Data folder does not exist: {folder_path}")
            return 0
        
        # Support multiple file formats
        file_patterns = ["*.txt", "*.csv", "*.md", "*.pdf"]
        document_files = []
        
        for pattern in file_patterns:
            document_files.extend(glob.glob(os.path.join(folder_path, pattern)))
        
        if not document_files:
            logger.warning(f"No documents found in {folder_path}")
            return 0
        
        processed_count = 0
        
        for file_path in document_files:
            try:
                processed_count += self._process_single_file(file_path, store, category)
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                self.ingestion_stats["failed_documents"] += 1
        
        return processed_count
    
    def _process_single_file(self, file_path: str, store, category: str) -> int:
        """
        Process a single document file.
        
        Args:
            file_path (str): Path to the document file
            store: Elasticsearch store for indexing
            category (str): Document category
            
        Returns:
            int: Number of chunks created from this document
        """
        logger.debug(f"Processing file: {file_path}")
        
        try:
            # Load document
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            if not documents:
                logger.warning(f"No content loaded from {file_path}")
                return 0
            
            total_chunks = 0
            
            for doc in documents:
                # Add metadata
                doc.metadata.update({
                    "source": file_path,
                    "category": category,
                    "filename": os.path.basename(file_path)
                })
                
                # Split document into chunks
                chunks = self.document_processor.split_document(doc.page_content)
                
                # Add chunks to store
                if chunks:
                    # Update metadata for each chunk
                    for i, chunk in enumerate(chunks):
                        chunk.metadata.update(doc.metadata)
                        chunk.metadata["chunk_id"] = i
                    
                    store.add_documents(chunks)
                    total_chunks += len(chunks)
                    self.ingestion_stats["total_chunks"] += len(chunks)
            
            self.ingestion_stats["total_documents"] += 1
            return total_chunks
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise IngestionError(f"Failed to process {file_path}: {e}")
    
    def ingest_from_text(self, text: str, category: str, store, 
                        metadata: Optional[Dict] = None) -> int:
        """
        Ingest text content directly without file loading.
        
        Args:
            text (str): Text content to ingest
            category (str): Document category
            store: Elasticsearch store for indexing
            metadata (Optional[Dict]): Additional metadata
            
        Returns:
            int: Number of chunks created
        """
        try:
            # Create base metadata
            doc_metadata = {
                "category": category,
                "source": "direct_input"
            }
            if metadata:
                doc_metadata.update(metadata)
            
            # Split text into chunks
            chunks = self.document_processor.split_document(text)
            
            # Add metadata to chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata.update(doc_metadata)
                chunk.metadata["chunk_id"] = i
            
            # Add to store
            if chunks:
                store.add_documents(chunks)
                self.ingestion_stats["total_chunks"] += len(chunks)
                logger.info(f"Successfully ingested {len(chunks)} chunks for category {category}")
            
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Failed to ingest text for category {category}: {e}")
            raise IngestionError(f"Text ingestion failed: {e}")
    
    def get_ingestion_stats(self) -> Dict[str, any]:
        """
        Get current ingestion statistics.
        
        Returns:
            Dict[str, any]: Ingestion statistics
        """
        return self.ingestion_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset ingestion statistics."""
        self.ingestion_stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "failed_documents": 0,
            "processed_by_category": {}
        }
