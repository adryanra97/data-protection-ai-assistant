"""
Search Engine Service

This module provides Elasticsearch-based search capabilities with Azure OpenAI embeddings
for the Data Protection AI Assistant.

Author: Adryan R A
"""

import logging
from typing import Optional, Dict, Any
from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import AzureOpenAIEmbeddings

from ..core.config import settings

logger = logging.getLogger(__name__)


class SearchEngineError(Exception):
    """Custom exception for search engine related errors."""
    pass


class SearchEngine:
    """
    Elasticsearch-based search engine with Azure OpenAI embeddings.
    
    This class manages Elasticsearch connections, index creation, and provides
    document stores for different legal document categories.
    """
    
    def __init__(self):
        """
        Initialize the search engine with Elasticsearch client and embeddings.
        
        Raises:
            SearchEngineError: If connection to Elasticsearch fails
        """
        try:
            self.es_client = Elasticsearch(
                [settings.ELASTICSEARCH_URL],
                api_key=settings.ELASTICSEARCH_API_KEY,
                verify_certs=True,
                request_timeout=30,
                retry_on_timeout=True,
                max_retries=3
            )
            
            # Test connection
            if not self.es_client.ping():
                raise SearchEngineError("Failed to connect to Elasticsearch")
                
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {e}")
            raise SearchEngineError(f"Elasticsearch initialization failed: {e}")
        
        try:
            self.embeddings = AzureOpenAIEmbeddings(
                openai_api_key=settings.OPENAI_EMBED_API_KEY,
                azure_endpoint=settings.EMBED_OPENAI_API_BASE,
                model=settings.EMBED_MODEL_NAME,
                openai_api_version="2023-05-15",
                chunk_size=1000
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI embeddings: {e}")
            raise SearchEngineError(f"Embeddings initialization failed: {e}")
    
    def get_store(self, index_name: str) -> ElasticsearchStore:
        """
        Get or create an Elasticsearch store for a specific index.
        
        Args:
            index_name (str): Name of the Elasticsearch index
            
        Returns:
            ElasticsearchStore: Configured Elasticsearch store instance
            
        Raises:
            SearchEngineError: If index creation or store initialization fails
        """
        try:
            if not self.es_client.indices.exists(index=index_name):
                logger.info(f"Creating new index: {index_name}")
                self._create_index(index_name)
            
            return ElasticsearchStore.from_documents(
                documents=[],
                embedding=self.embeddings,
                index_name=index_name,
                es_connection=self.es_client
            )
            
        except Exception as e:
            logger.error(f"Failed to get store for index {index_name}: {e}")
            raise SearchEngineError(f"Store creation failed for {index_name}: {e}")
    
    def _create_index(self, index_name: str) -> None:
        """
        Create a new Elasticsearch index with proper mapping for vector search.
        
        Args:
            index_name (str): Name of the index to create
            
        Raises:
            SearchEngineError: If index creation fails
        """
        mapping = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "knn": True,
                    "knn.algo_param.ef_search": 100
                }
            },
            "mappings": {
                "properties": {
                    "page_content": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "metadata": {
                        "type": "object",
                        "enabled": True
                    },
                    "vector": {
                        "type": "dense_vector",
                        "dims": 1536,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        
        try:
            self.es_client.indices.create(index=index_name, body=mapping)
            logger.info(f"Successfully created index: {index_name}")
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            raise SearchEngineError(f"Index creation failed: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Elasticsearch cluster.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            cluster_health = self.es_client.cluster.health()
            return {
                "status": "healthy",
                "cluster_name": cluster_health.get("cluster_name"),
                "cluster_status": cluster_health.get("status"),
                "number_of_nodes": cluster_health.get("number_of_nodes"),
                "active_shards": cluster_health.get("active_shards")
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific index.
        
        Args:
            index_name (str): Name of the index
            
        Returns:
            Dict[str, Any]: Index statistics
        """
        try:
            stats = self.es_client.indices.stats(index=index_name)
            index_stats = stats["indices"].get(index_name, {})
            
            return {
                "document_count": index_stats.get("total", {}).get("docs", {}).get("count", 0),
                "store_size": index_stats.get("total", {}).get("store", {}).get("size_in_bytes", 0),
                "index_exists": self.es_client.indices.exists(index=index_name)
            }
        except Exception as e:
            logger.warning(f"Failed to get stats for index {index_name}: {e}")
            return {
                "document_count": 0,
                "store_size": 0,
                "index_exists": False,
                "error": str(e)
            }
