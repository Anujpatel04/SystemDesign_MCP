"""
Application configuration with environment variable support.

Supports OpenAI, Azure OpenAI, and Ollama as LLM backends.
"""

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: Literal["openai", "azure", "ollama"] = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    # Azure OpenAI (use when LLM_PROVIDER=azure)
    azure_endpoint: str = ""  # e.g. https://oai-nasco.openai.azure.com
    azure_api_key: str = Field("", validation_alias=AliasChoices("AZURE_API_KEY", "AZURE_KEY"))
    azure_api_version: str = "2025-01-01-preview"
    azure_deployment: str = "gpt-4o"  # deployment name
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # App
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    streamlit_port: int = 8501

    # Optional load estimation
    default_qps_estimate: int = 1000
    default_storage_gb: int = 100


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
