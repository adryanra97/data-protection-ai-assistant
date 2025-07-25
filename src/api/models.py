"""
Pydantic Models for API Requests and Responses

This module defines the data models used in the API endpoints
for the Data Protection AI Assistant.

Author: Adryan R A
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class QueryRequest(BaseModel):
    """
    Model for legal question requests.
    
    This model validates and structures incoming questions to the AI assistant.
    """
    query: str = Field(
        ..., 
        min_length=3,
        max_length=2000,
        description="The legal question or query to be answered"
    )
    context: Optional[str] = Field(
        None,
        max_length=10000,
        description="Additional context or document content to consider"
    )
    
    @validator('query')
    def validate_query(cls, v):
        """Validate that query is not empty or just whitespace."""
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class QueryResponse(BaseModel):
    """
    Model for legal question responses.
    
    This model structures the AI assistant's responses to legal questions.
    """
    answer: str = Field(
        ...,
        description="The AI assistant's answer to the legal question"
    )
    sources_used: Optional[List[str]] = Field(
        None,
        description="List of sources used to generate the answer"
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score of the answer (0-1)"
    )
    processing_time: Optional[float] = Field(
        None,
        description="Time taken to process the query in seconds"
    )


class UploadResponse(BaseModel):
    """
    Model for document upload responses.
    
    This model structures responses from document upload operations.
    """
    status: str = Field(
        ...,
        description="Status of the upload operation"
    )
    message: str = Field(
        ...,
        description="Descriptive message about the upload result"
    )
    document_id: Optional[str] = Field(
        None,
        description="Unique identifier for the uploaded document"
    )
    chunks_created: Optional[int] = Field(
        None,
        ge=0,
        description="Number of chunks created from the document"
    )
    preview: Optional[str] = Field(
        None,
        max_length=500,
        description="Preview of the uploaded content"
    )


class ResetResponse(BaseModel):
    """
    Model for chat reset responses.
    
    This model structures responses from conversation reset operations.
    """
    status: str = Field(
        ...,
        description="Status of the reset operation"
    )
    message: str = Field(
        ...,
        description="Confirmation message for the reset"
    )


class HealthCheckResponse(BaseModel):
    """
    Model for health check responses.
    
    This model provides system health and status information.
    """
    status: str = Field(
        ...,
        description="Overall system status"
    )
    version: str = Field(
        ...,
        description="Application version"
    )
    services: Dict[str, Any] = Field(
        ...,
        description="Status of individual services"
    )
    uptime: Optional[float] = Field(
        None,
        description="Application uptime in seconds"
    )


class ConversationHistoryResponse(BaseModel):
    """
    Model for conversation history responses.
    
    This model structures the conversation history data.
    """
    history: List[Dict[str, str]] = Field(
        ...,
        description="List of previous conversation exchanges"
    )
    total_exchanges: int = Field(
        ...,
        ge=0,
        description="Total number of question-answer exchanges"
    )


class ErrorResponse(BaseModel):
    """
    Model for error responses.
    
    This model structures error messages returned by the API.
    """
    error: str = Field(
        ...,
        description="Error type or code"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    timestamp: Optional[str] = Field(
        None,
        description="ISO timestamp when error occurred"
    )


class SystemStatsResponse(BaseModel):
    """
    Model for system statistics responses.
    
    This model provides detailed system and usage statistics.
    """
    document_stores: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Statistics for each document store"
    )
    total_queries: int = Field(
        ...,
        ge=0,
        description="Total number of queries processed"
    )
    average_response_time: Optional[float] = Field(
        None,
        description="Average response time in seconds"
    )
    memory_usage: Optional[Dict[str, float]] = Field(
        None,
        description="Current memory usage statistics"
    )
