"""
Configuration Management Module

This module handles all configuration settings for the Data Protection AI Assistant,
including API keys, database connections, and model configurations.

Author: Adryan R A
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv


class Settings(BaseSettings):
    """
    Application settings and configuration management.
    
    This class manages all environment variables and configuration settings
    required for the Data Protection AI Assistant application.
    """
    
    # OpenAI Configuration
    OPENAI_CHAT_API_KEY: str = Field(..., env="OPENAI_CHAT_API_KEY", description="OpenAI API key for chat models")
    OPENAI_EMBED_API_KEY: str = Field(..., env="OPENAI_EMBED_API_KEY", description="OpenAI API key for embeddings")
    
    # Elasticsearch Configuration  
    ELASTICSEARCH_API_KEY: str = Field(..., env="ELASTICSEARCH_API_KEY", description="Elasticsearch API key")
    ELASTICSEARCH_URL: str = Field(..., env="ELASTICSEARCH_URL", description="Elasticsearch cluster URL")
    
    # Tavily Search Configuration
    TAVILY_API_URL: str = Field(..., env="TAVILY_API_URL", description="Tavily API endpoint URL")
    TAVILY_API_KEY: str = Field(..., env="TAVILY_API_KEY", description="Tavily API key for web search")
    
    # Azure OpenAI Configuration
    EMBED_OPENAI_API_BASE: str = Field(..., env="EMBED_OPENAI_API_BASE", description="Azure OpenAI base URL for embeddings")
    EMBED_MODEL_NAME: str = Field(..., env="EMBED_MODEL_NAME", description="Embedding model name")
    CHAT_OPENAI_API_BASE: str = Field(..., env="CHAT_OPENAI_API_BASE", description="Azure OpenAI base URL for chat")
    CHAT_MODEL_NAME: str = Field(..., env="CHAT_MODEL_NAME", description="Chat model deployment name")
    
    # Application Configuration
    DEBUG: bool = Field(default=False, env="DEBUG", description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    MAX_CHUNK_SIZE: int = Field(default=1500, env="MAX_CHUNK_SIZE", description="Maximum chunk size for document splitting")
    SEARCH_K: int = Field(default=3, env="SEARCH_K", description="Number of documents to retrieve in search")
    SEARCH_SCORE_THRESHOLD: float = Field(default=0.7, env="SEARCH_SCORE_THRESHOLD", description="Minimum similarity score for search results")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST", description="API server host")
    API_PORT: int = Field(default=8000, env="API_PORT", description="API server port")
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()
    
    @validator('SEARCH_SCORE_THRESHOLD')
    def validate_score_threshold(cls, v):
        """Validate search score threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError('SEARCH_SCORE_THRESHOLD must be between 0 and 1')
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def load_settings() -> Settings:
    """
    Load and return application settings.
    
    Returns:
        Settings: Configured application settings instance
    """
    load_dotenv()
    return Settings()


# Global settings instance
settings = load_settings()
