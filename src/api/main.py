"""
FastAPI Application - Data Protection AI Assistant

This module contains the main FastAPI application with all API endpoints
for the Data Protection AI Assistant.

Author: Adryan R A
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .models import (
    QueryRequest, QueryResponse, UploadResponse, ResetResponse,
    HealthCheckResponse, ConversationHistoryResponse, ErrorResponse,
    SystemStatsResponse
)
from ..services.search_engine import SearchEngine
from ..services.ingestion import DocumentIngestor
from ..agents.tools import ToolManager
from ..agents.qa_engine import QAEngine
from ..core.config import settings
from ..utils.logging_config import setup_logging
from ..utils.document_processor import DocumentProcessor

# Set up logging
setup_logging("logs/api.log")
logger = logging.getLogger(__name__)

# Global variables for dependency injection
search_engine: SearchEngine = None
document_ingestor: DocumentIngestor = None
tool_manager: ToolManager = None
qa_engine: QAEngine = None
app_start_time: float = None
query_count: int = 0
total_response_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    This function handles initialization of all services during startup
    and cleanup during shutdown.
    """
    global search_engine, document_ingestor, tool_manager, qa_engine, app_start_time
    
    # Startup
    logger.info("Starting Data Protection AI Assistant API...")
    app_start_time = time.time()
    
    try:
        # Initialize search engine
        logger.info("Initializing search engine...")
        search_engine = SearchEngine()
        
        # Initialize document stores
        logger.info("Setting up document stores...")
        stores = {
            "gdpr": search_engine.get_store("gdpr_docs"),
            "pdp": search_engine.get_store("uupdp_docs"),
            "company": search_engine.get_store("company_docs")
        }
        
        # Initialize document ingestor
        logger.info("Initializing document ingestor...")
        document_ingestor = DocumentIngestor(search_engine)
        
        # Ingest documents
        logger.info("Ingesting documents...")
        ingestion_stats = document_ingestor.ingest_all_documents(stores)
        logger.info(f"Document ingestion completed: {ingestion_stats}")
        
        # Initialize tools and QA engine
        logger.info("Setting up AI agents...")
        tool_manager = ToolManager(stores)
        qa_engine = QAEngine(tool_manager)
        
        logger.info("API startup completed successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down Data Protection AI Assistant API...")


# Create FastAPI application
app = FastAPI(
    title="Data Protection AI Assistant API",
    description="Multi-agent AI system for legal question answering focused on data privacy laws",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get QA engine
def get_qa_engine() -> QAEngine:
    """Dependency to provide QA engine instance."""
    if qa_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="QA Engine not initialized"
        )
    return qa_engine


# Dependency to get search engine
def get_search_engine() -> SearchEngine:
    """Dependency to provide search engine instance."""
    if search_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search Engine not initialized"
        )
    return search_engine


@app.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    qa: QAEngine = Depends(get_qa_engine)
) -> QueryResponse:
    """
    Process a legal question and return an AI-generated answer.
    
    This endpoint uses the multi-agent system to retrieve relevant information
    from legal documents and provide comprehensive answers.
    
    Args:
        request (QueryRequest): The legal question and optional context
        qa (QAEngine): QA engine dependency
        
    Returns:
        QueryResponse: The AI assistant's answer and metadata
        
    Raises:
        HTTPException: If query processing fails
    """
    global query_count, total_response_time
    
    start_time = time.time()
    
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        # Process the query
        answer = qa.answer(request.query, request.context)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update statistics
        query_count += 1
        total_response_time += processing_time
        
        logger.info(f"Query processed successfully in {processing_time:.2f} seconds")
        
        return QueryResponse(
            answer=answer,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = "user_upload",
    qa: QAEngine = Depends(get_qa_engine)
) -> UploadResponse:
    """
    Upload and process a legal document for context.
    
    This endpoint allows users to upload documents that will be processed
    and used as additional context for answering questions.
    
    Args:
        file (UploadFile): The document file to upload
        category (str): Category for the document (default: "user_upload")
        qa (QAEngine): QA engine dependency
        
    Returns:
        UploadResponse: Upload status and processing results
        
    Raises:
        HTTPException: If file upload or processing fails
    """
    try:
        logger.info(f"Processing uploaded file: {file.filename}")
        
        # Read and decode file content
        content = await file.read()
        
        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text_content = content.decode("latin-1")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to decode file. Please ensure it's a text file."
                )
        
        # Process document
        processor = DocumentProcessor()
        chunks = processor.split_document(text_content)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No processable content found in the uploaded file."
            )
        
        # Store for temporary use (you might want to implement proper storage)
        # For now, we'll just return success with preview
        preview = text_content[:500] + "..." if len(text_content) > 500 else text_content
        
        logger.info(f"Document processed successfully: {len(chunks)} chunks created")
        
        return UploadResponse(
            status="success",
            message=f"Document processed successfully. Created {len(chunks)} chunks.",
            chunks_created=len(chunks),
            preview=preview
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process uploaded file: {str(e)}"
        )


@app.post("/reset", response_model=ResetResponse)
async def reset_conversation(
    qa: QAEngine = Depends(get_qa_engine)
) -> ResetResponse:
    """
    Reset the conversation memory.
    
    This endpoint clears the conversation history and resets the AI assistant's
    memory for a fresh start.
    
    Args:
        qa (QAEngine): QA engine dependency
        
    Returns:
        ResetResponse: Confirmation of the reset operation
    """
    try:
        qa.reset_memory()
        logger.info("Conversation memory reset successfully")
        
        return ResetResponse(
            status="success",
            message="Conversation memory has been reset successfully."
        )
        
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset conversation: {str(e)}"
        )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check(
    search: SearchEngine = Depends(get_search_engine)
) -> HealthCheckResponse:
    """
    Perform a health check on all system components.
    
    This endpoint checks the status of all services and returns
    comprehensive health information.
    
    Returns:
        HealthCheckResponse: System health status and information
    """
    try:
        # Check search engine health
        es_health = search.health_check()
        
        # Calculate uptime
        uptime = time.time() - app_start_time if app_start_time else 0
        
        services = {
            "elasticsearch": es_health,
            "qa_engine": {"status": "healthy" if qa_engine else "unavailable"},
            "tool_manager": {"status": "healthy" if tool_manager else "unavailable"}
        }
        
        overall_status = "healthy" if all(
            service.get("status") == "healthy" for service in services.values()
        ) else "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            version="1.0.0",
            services=services,
            uptime=uptime
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            version="1.0.0",
            services={"error": str(e)},
            uptime=0
        )


@app.get("/conversation/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    qa: QAEngine = Depends(get_qa_engine)
) -> ConversationHistoryResponse:
    """
    Get the current conversation history.
    
    This endpoint returns the conversation history between the user
    and the AI assistant.
    
    Args:
        qa (QAEngine): QA engine dependency
        
    Returns:
        ConversationHistoryResponse: Conversation history and statistics
    """
    try:
        history = qa.get_conversation_history()
        
        return ConversationHistoryResponse(
            history=history,
            total_exchanges=len(history)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )


@app.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    search: SearchEngine = Depends(get_search_engine)
) -> SystemStatsResponse:
    """
    Get system statistics and usage information.
    
    This endpoint provides detailed statistics about document stores,
    query processing, and system performance.
    
    Returns:
        SystemStatsResponse: Comprehensive system statistics
    """
    try:
        # Get document store statistics
        store_names = ["gdpr_docs", "uupdp_docs", "company_docs"]
        document_stores = {}
        
        for store_name in store_names:
            stats = search.get_index_stats(store_name)
            document_stores[store_name] = stats
        
        # Calculate average response time
        avg_response_time = total_response_time / query_count if query_count > 0 else 0
        
        return SystemStatsResponse(
            document_stores=document_stores,
            total_queries=query_count,
            average_response_time=avg_response_time
        )
        
    except Exception as e:
        logger.error(f"Error retrieving system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system statistics: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred",
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.get("/openapi.json")
def custom_openapi():
    """Generate custom OpenAPI specification."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Data Protection AI Assistant API",
        version="1.0.0",
        description="Multi-agent AI system for legal question answering",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
