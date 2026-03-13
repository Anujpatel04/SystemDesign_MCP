"""
FastAPI application for the System Design MCP platform.

Provides REST endpoints to trigger design generation and retrieve results.
Optionally serves the React frontend from web/dist when built.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from system_design_mcp.core.mcp_controller import MCPController
from system_design_mcp.models.schemas import FormattedOutput
from system_design_mcp.utils.logger import get_logger


logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan: startup/shutdown."""
    logger.info("api_startup")
    yield
    logger.info("api_shutdown")


app = FastAPI(
    title="System Design MCP API",
    description="Generate system architecture, APIs, and diagrams from natural language prompts.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DesignRequest(BaseModel):
    """Request body for design generation."""

    prompt: str = Field(..., min_length=1, description="System design prompt (e.g. 'Design a scalable chat system like WhatsApp')")


class DesignResponse(BaseModel):
    """Full design response for API consumers."""

    system_overview: str
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    architecture_components: list[dict[str, Any]]
    infrastructure_stack: list[dict[str, Any]]
    api_design: list[dict[str, Any]]
    architecture_diagram_mermaid: str
    workflow_diagram_mermaid: str
    scaling_strategy: list[str]
    load_estimate: dict[str, Any] | None = None


def _formatted_to_response(out: FormattedOutput) -> DesignResponse:
    """Convert FormattedOutput to API response model."""
    return DesignResponse(
        system_overview=out.system_overview or "",
        functional_requirements=out.functional_requirements or [],
        non_functional_requirements=out.non_functional_requirements or [],
        architecture_components=[c.model_dump() for c in (out.architecture_components or [])],
        infrastructure_stack=[i.model_dump() for i in (out.infrastructure_stack or [])],
        api_design=[e.model_dump() for e in (out.api_design or [])],
        architecture_diagram_mermaid=out.architecture_diagram_mermaid or "",
        workflow_diagram_mermaid=out.workflow_diagram_mermaid or "",
        scaling_strategy=out.scaling_strategy or [],
        load_estimate=out.load_estimate,
    )


@app.post("/v1/design", response_model=DesignResponse)
async def generate_design(request: DesignRequest) -> DesignResponse:
    """
    Generate a full system design from a natural language prompt.
    Runs the full agent pipeline (requirements → architecture → infra → API → workflow → diagrams → formatter).
    """
    try:
        controller = MCPController()
        result = await controller.run(request.prompt.strip())
        return _formatted_to_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("design_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Design generation failed. Check logs.")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check for load balancers and monitoring."""
    return {"status": "ok"}


# Serve React frontend when web/dist exists (e.g. after npm run build from repo root)
_web_dist = Path(__file__).resolve().parents[2] / "web" / "dist"
if _web_dist.is_dir():
    app.mount("/assets", StaticFiles(directory=_web_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        from fastapi.responses import FileResponse
        if not full_path.startswith("v1/") and not full_path.startswith("health"):
            index = _web_dist / "index.html"
            if index.exists():
                return FileResponse(index)
        raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    from system_design_mcp.core.config import get_settings
    s = get_settings()
    uvicorn.run("system_design_mcp.api.main:app", host=s.api_host, port=s.api_port, reload=True)
