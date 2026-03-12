# System Design MCP Agent Platform

Production-grade **System Design MCP (Model Context Protocol) Agent Platform** that generates system architecture, component breakdowns, API structures, and workflow diagrams from natural language prompts.

## Features

- **Multi-agent pipeline**: Requirement Analyzer → Architecture Generator → Infrastructure Planner → API Design → Workflow Generator → Diagram Generator → Output Formatter
- **Dual LLM support**: OpenAI and local **Ollama** models
- **Structured outputs**: Functional/non-functional requirements, architecture components, infrastructure stack, REST API design, scaling strategy
- **Diagrams**: Mermaid **architecture** (flowchart) and **workflow** (sequence) diagrams, rendered in the UI
- **Streamlit UI**: Single text prompt → full design with export (Markdown)
- **FastAPI**: Optional REST API for programmatic access
- **Docker**: Single Dockerfile for deployment

## Project Structure

```
system_design_mcp/
├── agents/
│   ├── requirement_agent.py   # Requirement Analyzer
│   ├── architecture_agent.py # Architecture Generator
│   ├── infra_agent.py        # Infrastructure Planner
│   ├── api_agent.py          # API Design
│   ├── workflow_agent.py     # Workflow Generator
│   ├── diagram_agent.py      # Diagram Generator (Mermaid)
│   └── formatter_agent.py    # Output Formatter
├── core/
│   ├── config.py             # Settings (env)
│   └── mcp_controller.py     # Pipeline orchestration
├── models/
│   └── schemas.py            # Pydantic models
├── utils/
│   ├── logger.py             # Structured logging
│   ├── llm_client.py         # OpenAI / Ollama abstraction
│   └── mermaid_renderer.py   # Mermaid sanitization
├── frontend/
│   └── app.py                # Streamlit app
└── api/
    └── main.py               # FastAPI app
```

## Requirements

- Python 3.11+
- OpenAI API key (if using OpenAI) or running Ollama (if using local models)

## Setup

1. **Clone and enter project**

   ```bash
   cd /path/to/SystemDesign_MCP
   ```

2. **Create virtual environment and install dependencies**

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env:
   # - LLM_PROVIDER=openai or ollama
   # - If openai: OPENAI_API_KEY=sk-... and OPENAI_MODEL=gpt-4o
   # - If ollama: OLLAMA_BASE_URL=http://localhost:11434, OLLAMA_MODEL=llama3.2
   ```

## Run Locally

### Streamlit UI (recommended)

```bash
streamlit run system_design_mcp/frontend/app.py
```

Open http://localhost:8501, enter a prompt (e.g. *"Design a scalable chat system like WhatsApp"*), click **Generate Design**, and view requirements, architecture, infrastructure, API, diagrams, and scaling strategy. Use **Download Markdown** to export.

### FastAPI backend only

```bash
uvicorn system_design_mcp.api.main:app --host 0.0.0.0 --port 8000
```

- **POST /v1/design** – body: `{"prompt": "Design a ride sharing system like Uber"}` → full design JSON
- **GET /health** – health check

### Run from project root

Ensure the project root is on `PYTHONPATH` or run from repo root after `pip install -e .`:

```bash
# From repo root
python -m streamlit run system_design_mcp/frontend/app.py
```

## Docker

```bash
docker build -t system-design-mcp .
docker run -p 8501:8501 --env-file .env system-design-mcp
```

Streamlit will be available at http://localhost:8501. For API-only:

```bash
docker run -p 8000:8000 --env-file .env system-design-mcp \
  uvicorn system_design_mcp.api.main:app --host 0.0.0.0 --port 8000
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `openai` or `ollama` | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.2` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_HOST` / `API_PORT` | FastAPI host/port | `0.0.0.0` / `8000` |
| `STREAMLIT_PORT` | Streamlit port | `8501` |

## Export

- **Markdown**: Use **Download Markdown** in the Streamlit UI to get a single `.md` file with all sections and Mermaid code blocks.
- **JSON**: Use the FastAPI `POST /v1/design` endpoint; the response is full JSON (overview, requirements, components, infrastructure, API, Mermaid strings, scaling strategy).

## Optional: Load Estimation

The codebase is structured so you can add a **load estimation** module (e.g. in `utils/` or a dedicated agent) that estimates QPS, storage, and bandwidth from requirements and scale assumptions, and inject it into the formatter or API response.

## License

MIT.
