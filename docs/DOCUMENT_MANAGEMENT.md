# Document Management Feature

This document explains the new document management capabilities added to the Data Protection AI Assistant.

## Overview

The document management feature allows users to:
- Upload documents (CSV, TXT, XLSX, PDF) through the web interface
- Automatically chunk and index documents in Elasticsearch
- Activate/deactivate documents for use in RAG queries
- List and manage all uploaded documents
- Delete documents from the knowledge base

## API Endpoints

### Upload Document
```http
POST /documents/upload
Content-Type: multipart/form-data

Parameters:
- file (required): Document file to upload
- title (optional): Custom title for the document
- description (optional): Description of the document content
- category (optional): Document category (default: "user_upload")
```

### List Documents
```http
GET /documents?category={optional_category}

Response:
{
  "documents": [
    {
      "id": "doc_123",
      "title": "Document Title",
      "category": "user_upload",
      "chunk_count": 25,
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "description": "Document description"
    }
  ]
}
```

### Update Document Status
```http
PUT /documents/{document_id}/status
Content-Type: application/json

{
  "is_active": true
}
```

### Delete Document
```http
DELETE /documents/{document_id}
```

## Web Interface

### Chat Tab
- Main conversational interface
- Quick document upload for immediate use
- Chat history and conversation management

### Document Management Tab
- **Upload Section**: Upload new documents with metadata
- **Document Library**: View all uploaded documents
- **Document Controls**: Activate, deactivate, or delete documents

## Usage Examples

### 1. Upload a Legal Document
1. Go to the "Document Management" tab
2. Select a file (PDF, TXT, CSV, XLSX)
3. Add optional title and description
4. Choose appropriate category
5. Click "Upload Document"

### 2. Manage Document Status
1. View the document list to get the document ID
2. Copy the document ID
3. Use the controls to activate, deactivate, or delete

### 3. Use Documents in Chat
- Active documents are automatically included in RAG queries
- The AI will reference uploaded documents when relevant
- Inactive documents are ignored in searches

## File Format Support

### Supported Formats
- **TXT**: Plain text files
- **CSV**: Comma-separated values (processed as structured data)
- **XLSX**: Excel spreadsheets (all sheets processed)
- **PDF**: Portable Document Format (text extraction)

### Processing Details
- Documents are automatically chunked for optimal retrieval
- Metadata is preserved and searchable
- Embeddings are generated for semantic search
- Chunks are stored in Elasticsearch with full-text search capabilities

## Security Considerations

- File uploads are validated for type and size
- Content is processed server-side with sandboxing
- Document access is controlled through activation status
- All operations are logged for audit purposes

## Testing

Run the integration test to verify functionality:

```bash
python test_document_management.py
```

This test covers:
- Document upload
- Document listing
- Status activation/deactivation
- Document deletion
- Chat integration with document context

## Architecture

### Backend Components
- `DocumentManager`: Core document lifecycle management
- `DocumentProcessor`: File parsing and chunking
- `SearchEngine`: Elasticsearch integration
- API endpoints in `main.py`

### Frontend Components
- Gradio tabbed interface
- Document upload forms
- Management controls
- Status displays

### Data Flow
1. User uploads document via web interface
2. File is validated and processed
3. Content is chunked using LangChain splitters
4. Chunks are embedded and stored in Elasticsearch
5. Document metadata is indexed for management
6. RAG queries include active documents in search

## Configuration

### Environment Variables
```bash
# Elasticsearch configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password

# File upload limits
MAX_FILE_SIZE=10MB
ALLOWED_EXTENSIONS=txt,csv,xlsx,pdf
```

### Categories
- `user_upload`: User-uploaded documents (default)
- `gdpr`: GDPR-related documents
- `pdp`: Indonesia UU PDP documents  
- `company_policy`: Company policy documents
- `legal_doc`: Other legal documents

## Troubleshooting

### Common Issues

1. **Upload fails with timeout**
   - Check file size (limit: 10MB)
   - Verify Elasticsearch is running
   - Check server logs for errors

2. **Documents not appearing in search**
   - Ensure document is activated
   - Check Elasticsearch indexing status
   - Verify document contains processable text

3. **Chat not using uploaded documents**
   - Confirm documents are in "active" status
   - Check if question is relevant to document content
   - Verify RAG retrieval is working

### Debug Commands
```bash
# Check document count in Elasticsearch
curl -X GET "localhost:9200/documents/_count"

# View document management logs
tail -f logs/app.log | grep "DocumentManager"

# Test API endpoints directly
curl -X GET "http://localhost:8000/documents"
```

## Future Enhancements

- Batch document upload
- Document versioning
- Advanced search filters
- Document sharing between users
- OCR support for scanned documents
- Document similarity analysis
