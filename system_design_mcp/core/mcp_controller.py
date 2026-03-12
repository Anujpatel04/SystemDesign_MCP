"""
MCP Controller – orchestrates the system design pipeline.

Pipeline: User Prompt → Requirement Analyzer → Architecture Generator
→ Infrastructure Planner → API Designer → Workflow Generator
→ Diagram Generator → Output Formatter
"""

from typing import Any

from system_design_mcp.agents import (
    RequirementAnalyzerAgent,
    ArchitectureGeneratorAgent,
    InfrastructurePlannerAgent,
    APIDesignAgent,
    WorkflowGeneratorAgent,
    DiagramGeneratorAgent,
    OutputFormatterAgent,
)
from system_design_mcp.models.schemas import FormattedOutput
from system_design_mcp.utils.logger import get_logger


class MCPController:
    """
    Coordinates all agents in sequence to produce a full system design
    from a single user prompt.
    """

    def __init__(self) -> None:
        self._log = get_logger("MCPController")
        self._agents = [
            RequirementAnalyzerAgent(),
            ArchitectureGeneratorAgent(),
            InfrastructurePlannerAgent(),
            APIDesignAgent(),
            WorkflowGeneratorAgent(),
            DiagramGeneratorAgent(),
            OutputFormatterAgent(),
        ]

    async def run(self, user_prompt: str) -> FormattedOutput:
        """
        Execute the full pipeline and return the formatted system design.

        Raises:
            ValueError: If user_prompt is empty.
            Exception: Propagates the first agent or LLM error.
        """
        if not (user_prompt and user_prompt.strip()):
            raise ValueError("user_prompt cannot be empty")

        context: dict[str, Any] = {"user_prompt": user_prompt.strip()}

        for agent in self._agents:
            context = await agent.run(context)

        result = context.get("formatted_output")
        if not result or not isinstance(result, FormattedOutput):
            self._log.error("pipeline_missing_output", context_keys=list(context.keys()))
            raise RuntimeError("Pipeline did not produce formatted output")
        return result
