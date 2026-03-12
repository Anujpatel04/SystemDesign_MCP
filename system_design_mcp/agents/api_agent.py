"""
API Design Agent.

Generates REST API endpoints with method, path, description, request fields, and response structure.
"""

from typing import Any

from system_design_mcp.agents.base import BaseAgent
from system_design_mcp.models.schemas import APIEndpoint, APIDesignOutput
from system_design_mcp.utils.logger import log_agent_end, log_agent_start


SYSTEM_PROMPT = """You are an API architect. Given the system architecture and components,
design REST API endpoints.

Respond with a JSON object only (no markdown) with keys:
- "overview": one short paragraph on API design approach
- "endpoints": array of objects, each with:
  - "method": string (GET, POST, PUT, PATCH, DELETE)
  - "path": string (e.g. "/users/{id}", "/rides", "/payments")
  - "description": string (what the endpoint does)
  - "request_fields": array of objects with "name", "type", "required" (optional)
  - "response_structure": object or array describing the response (or string description)

Include key endpoints for the main entities and operations. Use plural nouns for resources."""


class APIDesignAgent(BaseAgent):
    """Generates REST API design from architecture and requirements."""

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        arch = context.get("architecture")
        req = context.get("requirement_analysis")
        if not arch:
            raise ValueError("architecture required in context")
        overview = getattr(arch, "overview", "") or str(arch)
        summary = getattr(req, "summary", "") if req else ""
        log_agent_start(self._log, "APIDesign", overview)

        user_msg = f"Architecture:\n{overview}\n\nRequirements:\n{summary}\n\nDesign REST API endpoints (method, path, description, request_fields, response_structure)."
        raw = await self._call_llm(SYSTEM_PROMPT, user_msg)
        data = self._extract_json(raw)
        if not data or not isinstance(data, dict):
            context["api_design"] = APIDesignOutput(overview=raw[:400] if raw else "", endpoints=[])
        else:
            endpoints: list[APIEndpoint] = []
            for e in data.get("endpoints") or []:
                if isinstance(e, dict) and e.get("path"):
                    endpoints.append(APIEndpoint(
                        method=(e.get("method") or "GET").upper(),
                        path=e["path"],
                        description=e.get("description") or "",
                        request_fields=e.get("request_fields") or [],
                        response_structure=e.get("response_structure") or {},
                    ))
            context["api_design"] = APIDesignOutput(
                overview=data.get("overview") or "",
                endpoints=endpoints,
            )
        log_agent_end(self._log, "APIDesign", success=True)
        return context
