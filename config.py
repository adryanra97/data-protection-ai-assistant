import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

class Settings(BaseSettings):
    OPENAI_CHAT_API_KEY: str = Field(..., env="OPENAI_CHAT_API_KEY")
    OPENAI_EMBED_API_KEY: str = Field(..., env="OPENAI_EMBED_API_KEY")
    ELASTICSEARCH_API_KEY: str = Field(..., env="ELASTICSEARCH_API_KEY")
    TAVILY_API_URL: str = Field(..., env="TAVILY_API_URL")
    TAVILY_API_KEY: str = Field(..., env="TAVILY_API_KEY")
    EMBED_OPENAI_API_BASE: str = Field(..., env="EMBED_OPENAI_API_BASE")
    EMBED_MODEL_NAME: str = Field(..., env="EMBED_MODEL_NAME")
    ELASTICSEARCH_URL: str = Field(..., env="ELASTICSEARCH_URL")
    CHAT_OPENAI_API_BASE: str = Field(..., env="CHAT_OPENAI_API_BASE")
    CHAT_MODEL_NAME: str = Field(..., env="CHAT_MODEL_NAME")

load_dotenv()
settings = Settings()
