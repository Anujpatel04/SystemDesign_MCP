"""
Diagram Generator Agent.

Generates Mermaid syntax for:
1. Architecture diagram (flowchart TD)
2. Workflow diagram (sequenceDiagram)
"""

from typing import Any

from system_design_mcp.agents.base import BaseAgent
from system_design_mcp.models.schemas import DiagramOutput
from system_design_mcp.utils.logger import log_agent_end, log_agent_start
from system_design_mcp.utils.mermaid_renderer import extract_mermaid


SYSTEM_PROMPT = """You are a technical diagram expert. Generate Mermaid diagrams only.

1) ARCHITECTURE DIAGRAM: Use flowchart TD (or graph TD). Nodes are system components (e.g. User, API Gateway, Auth Service, Ride Service). Use arrows with --> between nodes. Example:
flowchart TD
    User --> API_Gateway
    API_Gateway --> Auth_Service
    API_Gateway --> Ride_Service
    Ride_Service --> Driver_Service
    Ride_Service --> Payment_Service

2) WORKFLOW DIAGRAM: Use sequenceDiagram. Participants and messages for one key flow. Example:
sequenceDiagram
    participant User
    participant API as API Gateway
    participant Ride as Ride Service
    User->>API: Request Ride
    API->>Ride: Create Ride
    Ride->>User: Ride Confirmed

Output exactly two fenced code blocks:
First block: ```mermaid
flowchart TD
...
```
Second block: ```mermaid
sequenceDiagram
...
```"""


class DiagramGeneratorAgent(BaseAgent):
    """Generates Mermaid architecture and sequence diagrams from context."""

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        arch = context.get("architecture")
        workflow = context.get("workflow")
        if not arch:
            raise ValueError("architecture required in context")
        overview = getattr(arch, "overview", "") or str(arch)
        components = getattr(arch, "components", []) or []
        comp_names = [c.name if hasattr(c, "name") else str(c) for c in components]
        workflow_desc = str(getattr(workflow, "workflows", []) if workflow else [])
        log_agent_start(self._log, "DiagramGenerator", overview)

        user_msg = f"Architecture overview:\n{overview}\n\nComponents: {comp_names}\n\nWorkflow data:\n{workflow_desc}\n\nGenerate 1) flowchart TD architecture diagram, 2) sequenceDiagram workflow. Output only two mermaid code blocks."
        raw = await self._call_llm(SYSTEM_PROMPT, user_msg)
        arch_mermaid = extract_mermaid(raw, "flowchart")
        seq_mermaid = extract_mermaid(raw, "sequence")
        # If we got one block, try to split or use single type
        if not arch_mermaid and not seq_mermaid:
            arch_mermaid = extract_mermaid(raw, "any")
        context["diagram"] = DiagramOutput(
            architecture_mermaid=arch_mermaid,
            workflow_mermaid=seq_mermaid,
        )
        log_agent_end(self._log, "DiagramGenerator", success=True)
        return context
