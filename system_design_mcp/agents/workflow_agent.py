"""
Workflow Generator Agent.

Generates workflow descriptions and sequence logic for key operations (user flows, data flows, events).
"""

from typing import Any

from system_design_mcp.agents.base import BaseAgent
from system_design_mcp.models.schemas import WorkflowOutput
from system_design_mcp.utils.logger import log_agent_end, log_agent_start


SYSTEM_PROMPT = """You are a systems analyst. Given the architecture and API design,
describe key workflows as sequences of steps suitable for sequence diagrams.

Respond with a JSON object only (no markdown) with keys:
- "workflows": array of objects, each with:
  - "name": string (e.g. "Request Ride", "Process Payment")
  - "steps": array of objects with "actor", "target", "message" (e.g. User -> API Gateway: Request Ride)
- "sequence_descriptions": array of short strings, one per workflow, describing the flow in words

Use clear actor and target names that match the architecture (e.g. User, API Gateway, Ride Service, Driver App)."""


class WorkflowGeneratorAgent(BaseAgent):
    """Generates workflow sequences for diagram generation."""

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        arch = context.get("architecture")
        api = context.get("api_design")
        if not arch:
            raise ValueError("architecture required in context")
        overview = getattr(arch, "overview", "") or str(arch)
        api_overview = getattr(api, "overview", "") if api else ""
        log_agent_start(self._log, "WorkflowGenerator", overview)

        user_msg = f"Architecture:\n{overview}\n\nAPI context:\n{api_overview}\n\nDescribe 1-3 key workflows as sequence steps (actor, target, message) for sequence diagrams."
        raw = await self._call_llm(SYSTEM_PROMPT, user_msg)
        data = self._extract_json(raw)
        if not data or not isinstance(data, dict):
            context["workflow"] = WorkflowOutput(
                workflows=[],
                sequence_descriptions=[],
            )
        else:
            workflows = data.get("workflows") or []
            if not isinstance(workflows, list):
                workflows = []
            context["workflow"] = WorkflowOutput(
                workflows=workflows,
                sequence_descriptions=data.get("sequence_descriptions") or [],
            )
        log_agent_end(self._log, "WorkflowGenerator", success=True)
        return context
