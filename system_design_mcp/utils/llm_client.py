"""
LLM client abstraction supporting OpenAI and Ollama.

Provides a single interface for all agents to call LLMs.
"""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from system_design_mcp.core.config import get_settings


def get_llm() -> BaseChatModel:
    """Return the configured LLM (OpenAI or Ollama)."""
    settings = get_settings()
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key or None,
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
