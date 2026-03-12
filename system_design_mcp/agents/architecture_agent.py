"""
Architecture Generator Agent.

Generates system components (API Gateway, Auth, Services, Cache, Queue, etc.)
following distributed system best practices.
"""

from typing import Any

from system_design_mcp.agents.base import BaseAgent
from system_design_mcp.models.schemas import ArchitectureComponent, ArchitectureOutput
from system_design_mcp.utils.logger import log_agent_end, log_agent_start


SYSTEM_PROMPT = """You are a senior backend architect designing distributed systems.
Given the requirements summary, produce a list of system components.

Respond with a JSON object only (no markdown) with keys:
- "overview": one short paragraph describing the high-level architecture
- "components": array of objects, each with:
  - "name": string (e.g. "API Gateway", "Auth Service", "User Service", "Cache Layer")
  - "description": string (what it does)
  - "responsibilities": array of strings (bullet points)

Include typical components such as: API Gateway, Auth Service, core business services,
Notification Service, Search Service, Cache Layer, Message Queue, Database(s).
Reflect distributed system best practices (stateless services, separation of concerns)."""


class ArchitectureGeneratorAgent(BaseAgent):
    """Generates architecture components from requirements."""

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        req = context.get("requirement_analysis")
        if not req:
            raise ValueError("requirement_analysis required in context")
        summary = getattr(req, "summary", "") or str(req)
        log_agent_start(self._log, "ArchitectureGenerator", summary)

        user_msg = f"Requirements summary and context:\n\n{summary}\n\nGenerate architecture components."
        raw = await self._call_llm(SYSTEM_PROMPT, user_msg)
        data = self._extract_json(raw)
        if not data or not isinstance(data, dict):
            context["architecture"] = ArchitectureOutput(
                overview=raw[:400] if raw else "",
                components=[],
            )
        else:
            components: list[ArchitectureComponent] = []
            for c in data.get("components") or []:
                if isinstance(c, dict) and c.get("name"):
                    components.append(ArchitectureComponent(
                        name=c["name"],
                        description=c.get("description") or "",
                        responsibilities=c.get("responsibilities") or [],
                    ))
            context["architecture"] = ArchitectureOutput(
                overview=data.get("overview") or "",
                components=components,
            )
        log_agent_end(self._log, "ArchitectureGenerator", success=True)
        return context
