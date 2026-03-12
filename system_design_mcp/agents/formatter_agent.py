"""
Output Formatter Agent.

Combines all pipeline outputs into a single structured response:
System Overview, Requirements, Architecture, Infrastructure, API, Diagrams, Scaling Strategy.
"""

from typing import Any

from system_design_mcp.agents.base import BaseAgent
from system_design_mcp.core.config import get_settings
from system_design_mcp.models.schemas import (
    FormattedOutput,
    RequirementAnalysisOutput,
    ArchitectureOutput,
    ArchitectureComponent,
    InfrastructureOutput,
    InfrastructureItem,
    APIDesignOutput,
    APIEndpoint,
    DiagramOutput,
)
from system_design_mcp.utils.load_estimation import estimate_load
from system_design_mcp.utils.logger import log_agent_end, log_agent_start


SCALING_PROMPT = """Given the system design below, list 5-8 concise scaling strategies (horizontal scaling, caching, sharding, CDN, async processing, etc.). 
Reply with a JSON object: { "scaling_strategy": [ "item1", "item2", ... ] }
Only output the JSON, no markdown."""


class OutputFormatterAgent(BaseAgent):
    """Combines pipeline outputs and optionally enriches with scaling strategy."""

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        log_agent_start(self._log, "OutputFormatter", "formatting")
        req: RequirementAnalysisOutput | None = context.get("requirement_analysis")
        arch: ArchitectureOutput | None = context.get("architecture")
        infra: InfrastructureOutput | None = context.get("infrastructure")
        api: APIDesignOutput | None = context.get("api_design")
        diagram: DiagramOutput | None = context.get("diagram")

        system_overview = getattr(req, "summary", "") if req else ""
        functional = list(getattr(req, "functional_requirements", []) or []) if req else []
        non_functional = list(getattr(req, "non_functional_requirements", []) or []) if req else []
        components = list(getattr(arch, "components", []) or []) if arch else []
        if not all(isinstance(c, ArchitectureComponent) for c in components):
            components = [
                c if isinstance(c, ArchitectureComponent) else ArchitectureComponent(name=getattr(c, "name", str(c)), description=getattr(c, "description", ""), responsibilities=getattr(c, "responsibilities", []))
                for c in components
            ]
        infra_items = list(getattr(infra, "items", []) or []) if infra else []
        if not all(isinstance(i, InfrastructureItem) for i in infra_items):
            infra_items = [
                i if isinstance(i, InfrastructureItem) else InfrastructureItem(category=getattr(i, "category", ""), name=getattr(i, "name", ""), description=getattr(i, "description", ""), use_case=getattr(i, "use_case", ""))
                for i in infra_items
            ]
        api_endpoints = list(getattr(api, "endpoints", []) or []) if api else []
        if not all(isinstance(e, APIEndpoint) for e in api_endpoints):
            api_endpoints = [
                e if isinstance(e, APIEndpoint) else APIEndpoint(method=getattr(e, "method", "GET"), path=getattr(e, "path", ""), description=getattr(e, "description", ""), request_fields=getattr(e, "request_fields", []), response_structure=getattr(e, "response_structure", {}))
                for e in api_endpoints
            ]
        arch_mermaid = getattr(diagram, "architecture_mermaid", "") if diagram else ""
        workflow_mermaid = getattr(diagram, "workflow_mermaid", "") if diagram else ""

        # Optional: ask LLM for scaling strategy
        scaling: list[str] = []
        try:
            summary = f"Overview: {system_overview}. Components: {[c.name for c in components]}. Infra: {[i.name for i in infra_items]}."
            raw_scale = await self._call_llm(SCALING_PROMPT, summary)
            data = self._extract_json(raw_scale)
            if isinstance(data, dict) and data.get("scaling_strategy"):
                scaling = data["scaling_strategy"]
        except Exception:
            scaling = [
                "Horizontal scaling of stateless services",
                "Database read replicas and connection pooling",
                "Caching (e.g. Redis) for hot data",
                "Message queues for async processing",
                "CDN for static assets",
            ]

        # Optional load estimation
        settings = get_settings()
        load_est = None
        if req:
            try:
                le = estimate_load(
                    getattr(req, "scale_assumptions", []) or [],
                    getattr(req, "summary", "") or "",
                    default_qps=settings.default_qps_estimate,
                    default_storage_gb=settings.default_storage_gb,
                )
                load_est = {
                    "qps_estimate": le.qps_estimate,
                    "qps_note": le.qps_note,
                    "storage_gb_estimate": le.storage_gb_estimate,
                    "storage_note": le.storage_note,
                    "bandwidth_mbps_estimate": le.bandwidth_mbps_estimate,
                    "bandwidth_note": le.bandwidth_note,
                }
            except Exception:
                pass

        formatted = FormattedOutput(
            system_overview=system_overview,
            functional_requirements=functional,
            non_functional_requirements=non_functional,
            architecture_components=components,
            infrastructure_stack=infra_items,
            api_design=api_endpoints,
            architecture_diagram_mermaid=arch_mermaid,
            workflow_diagram_mermaid=workflow_mermaid,
            scaling_strategy=scaling,
            load_estimate=load_est,
            raw={
                "requirement_analysis": req.model_dump() if req else {},
                "architecture": arch.model_dump() if arch else {},
                "infrastructure": infra.model_dump() if infra else {},
                "api_design": api.model_dump() if api else {},
                "diagram": diagram.model_dump() if diagram else {},
            },
        )
        context["formatted_output"] = formatted
        log_agent_end(self._log, "OutputFormatter", success=True)
        return context
