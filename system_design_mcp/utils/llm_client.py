"""
LLM client abstraction supporting OpenAI, Azure OpenAI, and Ollama.

Provides a single interface for all agents to call LLMs.
"""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from system_design_mcp.core.config import get_settings


def get_llm() -> BaseChatModel:
    """Return the configured LLM (OpenAI, Azure OpenAI, or Ollama)."""
    settings = get_settings()
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key or None,
            temperature=0.3,
        )
    if settings.llm_provider == "azure":
        from urllib.parse import urlparse
        from langchain_openai import AzureChatOpenAI
        # Use base origin only (LangChain expects e.g. https://oai-nasco.openai.azure.com)
        endpoint = settings.azure_endpoint.strip()
        if "/openai/" in endpoint or "deployments" in endpoint:
            parsed = urlparse(endpoint)
            endpoint = f"{parsed.scheme}://{parsed.netloc}"
        endpoint = endpoint.rstrip("/")
        return AzureChatOpenAI(
            azure_endpoint=endpoint,
            api_key=settings.azure_api_key,
            api_version=settings.azure_api_version,
            azure_deployment=settings.azure_deployment,
            temperature=0.3,
        )
    if settings.llm_provider == "ollama":
        from langchain_community.chat_models.ollama import ChatOllama
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.3,
        )
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


async def invoke_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """
    Invoke the configured LLM with system and user prompts.
    Returns the content string of the response.
    """
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = await llm.ainvoke(messages)
    return response.content if hasattr(response, "content") else str(response)
