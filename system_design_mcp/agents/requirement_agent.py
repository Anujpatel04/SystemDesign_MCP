"""
Requirement Analyzer Agent.

Extracts functional and non-functional requirements, scale assumptions,
latency and availability expectations from a system design prompt.
"""

from typing import Any

from system_design_mcp.agents.base import BaseAgent
from system_design_mcp.models.schemas import RequirementAnalysisOutput
from system_design_mcp.utils.logger import log_agent_end, log_agent_start


SYSTEM_PROMPT = """You are a senior systems engineer analyzing system design prompts.
Extract structured requirements from the user's description.

Respond with a JSON object only (no markdown, no explanation) with exactly these keys:
- "functional_requirements": list of strings (user-facing features and capabilities)
- "non_functional_requirements": list of strings (scalability, reliability, security, performance)
- "scale_assumptions": list of strings (expected QPS, users, data volume if mentioned or implied)
- "latency_requirements": list of strings (response time, real-time needs)
- "availability_expectations": list of strings (uptime, SLA, fault tolerance)
- "summary": one short paragraph summarizing the system goal

Be specific and actionable. Infer reasonable assumptions when not stated."""


class RequirementAnalyzerAgent(BaseAgent):
    """Extracts structured requirements from a natural language system design prompt."""

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        prompt = context.get("user_prompt", "")
        if not prompt:
            raise ValueError("user_prompt required in context")
        log_agent_start(self._log, "RequirementAnalyzer", prompt)

        user_msg = f"System design prompt:\n\n{prompt}"
        raw = await self._call_llm(SYSTEM_PROMPT, user_msg)
        data = self._extract_json(raw)
        if not data or not isinstance(data, dict):
            # Fallback: build minimal output from raw text
            context["requirement_analysis"] = RequirementAnalysisOutput(
                summary=raw[:500] if raw else "Requirements could not be parsed.",
                functional_requirements=[],
                non_functional_requirements=[],
                scale_assumptions=[],
                latency_requirements=[],
                availability_expectations=[],
            )
        else:
            context["requirement_analysis"] = RequirementAnalysisOutput(
                functional_requirements=data.get("functional_requirements") or [],
                non_functional_requirements=data.get("non_functional_requirements") or [],
                scale_assumptions=data.get("scale_assumptions") or [],
                latency_requirements=data.get("latency_requirements") or [],
                availability_expectations=data.get("availability_expectations") or [],
                summary=data.get("summary") or "",
            )
        log_agent_end(self._log, "RequirementAnalyzer", success=True)
        return context
