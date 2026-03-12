"""
Infrastructure Planner Agent.

Suggests databases, caches, queues, object storage, search engines, and monitoring tools.
"""

from typing import Any

from system_design_mcp.agents.base import BaseAgent
from system_design_mcp.models.schemas import InfrastructureItem, InfrastructureOutput
from system_design_mcp.utils.logger import log_agent_end, log_agent_start


SYSTEM_PROMPT = """You are an infrastructure architect. Given the system architecture and requirements,
suggest concrete infrastructure choices.

Respond with a JSON object only (no markdown) with keys:
- "overview": one short paragraph on infrastructure strategy
- "items": array of objects, each with:
  - "category": string (e.g. "Database", "Cache", "Queue", "Object Storage", "Search", "Monitoring")
  - "name": string (e.g. "PostgreSQL", "Redis", "Kafka", "S3", "Elasticsearch", "Prometheus")
  - "description": string (why this choice)
  - "use_case": string (what it is used for in this system)

Suggest specific technologies: e.g. PostgreSQL, Redis, Kafka, Elasticsearch, S3, Prometheus/Grafana."""


class InfrastructurePlannerAgent(BaseAgent):
    """Suggests infrastructure stack from architecture and requirements."""

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        arch = context.get("architecture")
        req = context.get("requirement_analysis")
        if not arch:
            raise ValueError("architecture required in context")
        overview = getattr(arch, "overview", "") or str(arch)
        summary = getattr(req, "summary", "") if req else ""
        log_agent_start(self._log, "InfrastructurePlanner", overview)

        user_msg = f"Architecture overview:\n{overview}\n\nRequirements summary:\n{summary}\n\nSuggest infrastructure stack (databases, cache, queue, storage, search, monitoring)."
        raw = await self._call_llm(SYSTEM_PROMPT, user_msg)
        data = self._extract_json(raw)
        if not data or not isinstance(data, dict):
            context["infrastructure"] = InfrastructureOutput(
                overview=raw[:400] if raw else "",
                items=[],
            )
        else:
            items: list[InfrastructureItem] = []
            for i in data.get("items") or []:
                if isinstance(i, dict) and i.get("name"):
                    items.append(InfrastructureItem(
                        category=i.get("category") or "Other",
                        name=i["name"],
                        description=i.get("description") or "",
                        use_case=i.get("use_case") or "",
                    ))
            context["infrastructure"] = InfrastructureOutput(
                overview=data.get("overview") or "",
                items=items,
            )
        log_agent_end(self._log, "InfrastructurePlanner", success=True)
        return context
