"""
Document Processing Utilities

This module provides utilities for processing legal documents, including
text splitting, cleaning, and metadata extraction.

Author: Adryan R A
"""

import re
import logging
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document

from ..core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Custom exception for document processing errors."""
    pass


class DocumentProcessor:
    """
    Utility class for processing legal documents.
    
    This class provides methods for splitting documents into chunks,
    cleaning text, and extracting metadata from legal documents.
    """
    
    def __init__(self, max_chunk_size: Optional[int] = None):
        """
        Initialize the document processor.
        
        Args:
            max_chunk_size (Optional[int]): Maximum size for document chunks.
                                          Defaults to settings.MAX_CHUNK_SIZE
        """
        self.max_chunk_size = max_chunk_size or settings.MAX_CHUNK_SIZE
        self.min_chunk_size = 100  # Minimum viable chunk size
        self.overlap_size = 150    # Overlap between chunks for context preservation
    
    def split_document(self, text: str, metadata: Optional[Dict] = None) -> List[Document]:
        """
        Split a document into smaller chunks for better retrieval.
        
        This method uses a semantic-aware splitting approach that tries to
        preserve paragraph boundaries and legal structure.
        
        Args:
            text (str): Document text to split
            metadata (Optional[Dict]): Additional metadata for chunks
            
        Returns:
            List[Document]: List of document chunks
            
        Raises:
            DocumentProcessingError: If text processing fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for splitting")
            return []
        
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Split into initial chunks based on structure
            raw_chunks = self._structural_split(cleaned_text)
            
            # Process chunks to meet size requirements
            final_chunks = []
            for i, chunk_text in enumerate(raw_chunks):
                if len(chunk_text.strip()) < self.min_chunk_size:
                    # Merge small chunks with next chunk if possible
                    if i + 1 < len(raw_chunks):
                        raw_chunks[i + 1] = chunk_text + "\n\n" + raw_chunks[i + 1]
                    continue
                
                # Handle oversized chunks
                if len(chunk_text) > self.max_chunk_size:
                    sub_chunks = self._split_large_chunk(chunk_text)
                    for sub_chunk in sub_chunks:
                        if len(sub_chunk.strip()) >= self.min_chunk_size:
                            final_chunks.append(sub_chunk.strip())
                else:
                    final_chunks.append(chunk_text.strip())
            
            # Convert to Document objects
            documents = []
            for i, chunk in enumerate(final_chunks):
                doc_metadata = {"chunk_index": i, "chunk_size": len(chunk)}
                if metadata:
                    doc_metadata.update(metadata)
                
                documents.append(Document(
                    page_content=chunk,
                    metadata=doc_metadata
                ))
            
            logger.debug(f"Split document into {len(documents)} chunks")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to split document: {e}")
            raise DocumentProcessingError(f"Document splitting failed: {e}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize document text.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Remove excessive empty lines but preserve paragraph structure
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Clean up special characters that might interfere with processing
        text = re.sub(r'[^\w\s\n.,;:!?()\-\'"/@#$%&*+=<>{}[\]|\\~`]', ' ', text)
        
        return text.strip()
    
    def _structural_split(self, text: str) -> List[str]:
        """
        Split text based on structural elements like paragraphs and sections.
        
        Args:
            text (str): Text to split
            
        Returns:
            List[str]: List of text chunks
        """
        # Legal documents often have numbered sections, articles, etc.
        # Try to split on these structural elements first
        
        # Split on double line breaks (paragraphs)
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if adding this paragraph would exceed size limit
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(potential_chunk) <= self.max_chunk_size:
                current_chunk = potential_chunk
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with current paragraph
                current_chunk = paragraph
        
        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_large_chunk(self, text: str) -> List[str]:
        """
        Split a large chunk into smaller pieces.
        
        Args:
            text (str): Large text chunk to split
            
        Returns:
            List[str]: List of smaller chunks
        """
        # Try to split on sentence boundaries first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) <= self.max_chunk_size:
                current_chunk = potential_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If single sentence is too long, split it forcefully
                if len(sentence) > self.max_chunk_size:
                    word_chunks = self._split_by_words(sentence)
                    chunks.extend(word_chunks)
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_by_words(self, text: str) -> List[str]:
        """
        Split text by words when other methods fail.
        
        Args:
            text (str): Text to split
            
        Returns:
            List[str]: List of word-based chunks
        """
        words = text.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            potential_chunk = current_chunk + " " + word if current_chunk else word
            
            if len(potential_chunk) <= self.max_chunk_size:
                current_chunk = potential_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_legal_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract legal document metadata from text.
        
        Args:
            text (str): Document text
            
        Returns:
            Dict[str, Any]: Extracted metadata
        """
        metadata = {}
        
        # Look for article/section numbers
        article_pattern = r'(Article|Section|Article|Pasal)\s+(\d+)'
        articles = re.findall(article_pattern, text, re.IGNORECASE)
        if articles:
            metadata['contains_articles'] = [f"{article[0]} {article[1]}" for article in articles]
        
        # Look for legal references
        legal_ref_pattern = r'(GDPR|UU\s+PDP|Regulation|Directive)\s+[\d/\-\w]*'
        references = re.findall(legal_ref_pattern, text, re.IGNORECASE)
        if references:
            metadata['legal_references'] = list(set(references))
        
        # Estimate document type based on content
        if re.search(r'gdpr|general data protection regulation', text, re.IGNORECASE):
            metadata['document_type'] = 'GDPR'
        elif re.search(r'uu\s+pdp|undang.*undang.*perlindungan.*data', text, re.IGNORECASE):
            metadata['document_type'] = 'UU PDP'
        elif re.search(r'company|corporate|internal|policy', text, re.IGNORECASE):
            metadata['document_type'] = 'Company Policy'
        
        # Count key legal terms
        key_terms = ['personal data', 'privacy', 'consent', 'processing', 'controller', 'processor']
        term_counts = {}
        for term in key_terms:
            count = len(re.findall(term, text, re.IGNORECASE))
            if count > 0:
                term_counts[term] = count
        
        if term_counts:
            metadata['key_terms'] = term_counts
        
        return metadata
