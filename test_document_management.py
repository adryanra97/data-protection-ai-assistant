#!/usr/bin/env python3
"""
Test Script for Document Management Feature

This script tests the new document management functionality including
upload, list, activate/deactivate, and delete operations.

Author: Adryan R A
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_DOCUMENT_CONTENT = """
# Sample Legal Document

## Data Protection Compliance

This document outlines key data protection principles:

1. Lawfulness, fairness and transparency
2. Purpose limitation  
3. Data minimisation
4. Accuracy
5. Storage limitation
6. Integrity and confidentiality
7. Accountability

### GDPR Article 6 Legal Bases:
- Consent
- Contract
- Legal obligation
- Vital interests
- Public task
- Legitimate interests

This is a test document for the document management system.
"""

def test_document_management():
    """Test the complete document management workflow."""
    
    print("Testing Document Management Feature")
    print("=" * 50)
    
    # Check API health
    print("1. Checking API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("API is healthy")
        else:
            print(f"API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"Cannot connect to API: {e}")
        return
    
    # Create test file
    test_file_path = Path("test_document.txt")
    with open(test_file_path, "w") as f:
        f.write(TEST_DOCUMENT_CONTENT)
    
    document_id = None
    
    try:
        # Test 1: Upload document
        print("\\n2. Testing document upload...")
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            data = {
                "title": "Test Legal Document",
                "description": "A test document for data protection principles",
                "category": "user_upload"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/documents/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            document_id = result["document"]["id"]
            print(f"Document uploaded successfully!")
            print(f"   Title: {result['document']['title']}")
            print(f"   ID: {document_id}")
            print(f"   Chunks: {result['document']['chunk_count']}")
        else:
            print(f"Upload failed: {response.status_code} - {response.text}")
            return
        
        # Test 2: List documents
        print("\\n3. Testing document listing...")
        response = requests.get(f"{API_BASE_URL}/documents", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            docs = result["documents"]
            print(f"Found {len(docs)} document(s)")
            for doc in docs:
                print(f"   {doc['title']} (ID: {doc['id']}, Active: {doc['is_active']})")
        else:
            print(f"List failed: {response.status_code}")

        # Test 3: Deactivate document
        print("\\n4. Testing document deactivation...")
        response = requests.put(
            f"{API_BASE_URL}/documents/{document_id}/status",
            json={"is_active": False},
            timeout=10
        )
        
        if response.status_code == 200:
            print("Document deactivated successfully")
        else:
            print(f"Deactivation failed: {response.status_code}")

        # Test 4: Activate document
        print("\\n5. Testing document activation...")
        response = requests.put(
            f"{API_BASE_URL}/documents/{document_id}/status",
            json={"is_active": True},
            timeout=10
        )
        
        if response.status_code == 200:
            print("Document activated successfully")
        else:
            print(f"Activation failed: {response.status_code}")

        # Test 5: Test chat with document context
        print("\\n6. Testing chat with document context...")
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json={
                "question": "What are the main data protection principles mentioned in the uploaded document?",
                "conversation_id": "test_session"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Chat with document context successful")
            print(f"   Response preview: {result['answer'][:200]}...")
        else:
            print(f"Chat failed: {response.status_code}")
        
        # Test 6: Delete document
        print("\\n7. Testing document deletion...")
        response = requests.delete(f"{API_BASE_URL}/documents/{document_id}", timeout=10)
        
        if response.status_code == 200:
            print("Document deleted successfully")
        else:
            print(f"Deletion failed: {response.status_code}")

        print("\\nAll tests completed!")
        
    except Exception as e:
        print(f"Test error: {e}")

    finally:
        # Cleanup
        if test_file_path.exists():
            test_file_path.unlink()
            print("\\n🧹 Cleaned up test file")

if __name__ == "__main__":
    test_document_management()
