"""
Pydantic schemas for all agent inputs and outputs.

Ensures typed, validated data flow between agents and the pipeline.
"""

from typing import Any

from pydantic import BaseModel, Field


# --- Requirement Analyzer ---


class RequirementAnalysisOutput(BaseModel):
    """Structured output from the Requirement Analyzer Agent."""

    functional_requirements: list[str] = Field(default_factory=list)
    non_functional_requirements: list[str] = Field(default_factory=list)
    scale_assumptions: list[str] = Field(default_factory=list)
    latency_requirements: list[str] = Field(default_factory=list)
    availability_expectations: list[str] = Field(default_factory=list)
    summary: str = ""


# --- Architecture Generator ---


class ArchitectureComponent(BaseModel):
    """A single component in the system architecture."""

    name: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)


class ArchitectureOutput(BaseModel):
    """Output from the Architecture Generator Agent."""

    components: list[ArchitectureComponent] = Field(default_factory=list)
    overview: str = ""


# --- Infrastructure Planner ---


class InfrastructureItem(BaseModel):
    """A single infrastructure suggestion."""

    category: str  # e.g. "Database", "Cache", "Queue"
    name: str
    description: str
    use_case: str = ""


class InfrastructureOutput(BaseModel):
    """Output from the Infrastructure Planner Agent."""

    items: list[InfrastructureItem] = Field(default_factory=list)
    overview: str = ""


# --- API Design ---


class APIEndpoint(BaseModel):
    """A single REST API endpoint."""

    method: str  # GET, POST, PUT, PATCH, DELETE
    path: str
    description: str
    request_fields: list[dict[str, Any]] = Field(default_factory=list)
    response_structure: dict[str, Any] | list[Any] | str = Field(default_factory=dict)


class APIDesignOutput(BaseModel):
    """Output from the API Design Agent."""

    endpoints: list[APIEndpoint] = Field(default_factory=list)
    overview: str = ""


# --- Workflow Generator ---


class WorkflowStep(BaseModel):
    """A step in a workflow (for sequence diagrams)."""

    actor: str
    target: str
    message: str


class WorkflowOutput(BaseModel):
    """Output from the Workflow Generator Agent."""

    workflows: list[dict[str, Any]] = Field(default_factory=list)  # name -> list of steps
    sequence_descriptions: list[str] = Field(default_factory=list)


# --- Diagram Generator ---


class DiagramOutput(BaseModel):
    """Output from the Diagram Generator Agent."""

    architecture_mermaid: str = ""  # flowchart TD ...
    workflow_mermaid: str = ""  # sequenceDiagram ...


# --- Output Formatter (final combined output) ---


class FormattedOutput(BaseModel):
    """Final combined output from the Output Formatter Agent."""

    system_overview: str = ""
    functional_requirements: list[str] = Field(default_factory=list)
    non_functional_requirements: list[str] = Field(default_factory=list)
    architecture_components: list[ArchitectureComponent] = Field(default_factory=list)
    infrastructure_stack: list[InfrastructureItem] = Field(default_factory=list)
    api_design: list[APIEndpoint] = Field(default_factory=list)
    architecture_diagram_mermaid: str = ""
    workflow_diagram_mermaid: str = ""
    scaling_strategy: list[str] = Field(default_factory=list)
    load_estimate: dict[str, Any] | None = None  # optional QPS, storage, bandwidth
    raw: dict[str, Any] = Field(default_factory=dict)
