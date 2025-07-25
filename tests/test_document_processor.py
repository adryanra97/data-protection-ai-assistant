"""
Unit Tests for Document Processor

Test cases for the document processing utilities.

Author: Adryan R A
"""

import pytest
from src.utils.document_processor import DocumentProcessor, DocumentProcessingError


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DocumentProcessor(max_chunk_size=500)
    
    def test_initialization(self):
        """Test DocumentProcessor initialization."""
        assert self.processor.max_chunk_size == 500
        assert self.processor.min_chunk_size == 100
        assert self.processor.overlap_size == 150
    
    def test_split_document_basic(self):
        """Test basic document splitting."""
        text = "This is a test document.\n\nIt has multiple paragraphs.\n\nEach paragraph should be processed correctly."
        
        chunks = self.processor.split_document(text)
        
        assert len(chunks) > 0
        assert all(chunk.page_content for chunk in chunks)
        assert all(hasattr(chunk, 'metadata') for chunk in chunks)
    
    def test_split_document_empty(self):
        """Test splitting empty or whitespace-only text."""
        assert self.processor.split_document("") == []
        assert self.processor.split_document("   ") == []
        assert self.processor.split_document("\n\n\n") == []
    
    def test_split_document_large(self):
        """Test splitting large documents."""
        # Create a large document
        large_text = "This is a sentence. " * 100  # ~2000 characters
        
        chunks = self.processor.split_document(large_text)
        
        assert len(chunks) > 1
        assert all(len(chunk.page_content) <= self.processor.max_chunk_size for chunk in chunks)
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "This  has   excessive\n\n\n\nwhitespace\r\nand\rline\tbreaks."
        
        cleaned = self.processor._clean_text(dirty_text)
        
        assert "  " not in cleaned  # No double spaces
        assert "\r" not in cleaned  # No carriage returns
        assert "\n\n\n" not in cleaned  # No excessive newlines
    
    def test_extract_legal_metadata(self):
        """Test legal metadata extraction."""
        text = """
        Article 6 of the GDPR states that processing is lawful.
        Section 25 of UU PDP requires consent for data processing.
        This document discusses personal data protection.
        """
        
        metadata = self.processor.extract_legal_metadata(text)
        
        assert 'contains_articles' in metadata
        assert 'legal_references' in metadata
        assert 'key_terms' in metadata
        
    def test_split_document_with_metadata(self):
        """Test document splitting with custom metadata."""
        text = "Test document with metadata."
        custom_metadata = {"source": "test", "category": "legal"}
        
        chunks = self.processor.split_document(text, metadata=custom_metadata)
        
        assert len(chunks) == 1
        assert chunks[0].metadata["source"] == "test"
        assert chunks[0].metadata["category"] == "legal"
        assert "chunk_index" in chunks[0].metadata
