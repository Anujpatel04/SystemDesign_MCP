"""Base agent interface and shared helpers."""

import json
import re
from abc import ABC, abstractmethod
from typing import Any

from system_design_mcp.utils.logger import get_logger
from system_design_mcp.utils.llm_client import invoke_llm


class BaseAgent(ABC):
    """Base class for all pipeline agents."""

    def __init__(self) -> None:
        self._log = get_logger(self.__class__.__name__)

    @abstractmethod
    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent and return updated context with output."""
        ...

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call LLM and return content. Logs and raises on failure."""
        try:
            return await invoke_llm(system_prompt, user_prompt)
        except Exception as e:
            self._log.error("llm_call_failed", error=str(e), agent=self.__class__.__name__)
            raise

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any] | list[Any] | None:
        """Extract JSON object or array from markdown code block or raw text."""
        text = text.strip()
        # Try ```json ... ```
        code_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if code_match:
            raw = code_match.group(1).strip()
        else:
            raw = text
        # Find first { or [
        start_obj = raw.find("{")
        start_arr = raw.find("[")
        if start_obj == -1 and start_arr == -1:
            return None
        if start_arr >= 0 and (start_obj == -1 or start_arr < start_obj):
            start = start_arr
            end = raw.rfind("]") + 1
        else:
            start = start_obj
            end = raw.rfind("}") + 1
        if end <= start:
            return None
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            return None
