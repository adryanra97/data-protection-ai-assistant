from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import AzureOpenAIEmbeddings
from config import settings

class SearchEngine:
    def __init__(self):
        self.es_client = Elasticsearch(
            [settings.ELASTICSEARCH_URL],
            api_key=settings.ELASTICSEARCH_API_KEY
        )
        self.embeddings = AzureOpenAIEmbeddings(
            openai_api_key=settings.OPENAI_EMBED_API_KEY,
            azure_endpoint=settings.EMBED_OPENAI_API_BASE,
            model=settings.EMBED_MODEL_NAME,
            openai_api_version="2023-05-15"
        )

    def get_store(self, name: str) -> ElasticsearchStore:
        if not self.es_client.indices.exists(index=name):
            mapping = {
                "settings": {"index": {"vector_search": {"cosine": {}}}},
                "mappings": {"properties": {
                    "page_content": {"type": "text"},
                    "embedding": {"type": "dense_vector", "dims": 1536, "index": True, "similarity": "cosine"}
                }}
            }
            self.es_client.indices.create(index=name, body=mapping)
        return ElasticsearchStore.from_documents(
            documents=[],
            embedding=self.embeddings,
            index_name=name,
            es_connection=self.es_client
        )
