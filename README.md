# System Design MCP Agent Platform

Production-grade **System Design MCP (Model Context Protocol) Agent Platform** that generates system architecture, component breakdowns, API structures, and workflow diagrams from natural language prompts.

## Features

- **Multi-agent pipeline**: Requirement Analyzer → Architecture Generator → Infrastructure Planner → API Design → Workflow Generator → Diagram Generator → Output Formatter
- **LLM support**: **OpenAI**, **Azure OpenAI**, and local **Ollama** models
- **Structured outputs**: Functional/non-functional requirements, architecture components, infrastructure stack, REST API design, scaling strategy
- **Diagrams**: Mermaid **architecture** (flowchart) and **workflow** (sequence) diagrams, rendered in the UI
- **React frontend**: Professional, interactive UI (Vite + TypeScript + Tailwind) with export (Markdown)
- **FastAPI**: REST API and optional static serving of the built frontend
- **Docker**: Single Dockerfile for deployment

## Project Structure

```
├── web/                        # React frontend (Vite + TypeScript + Tailwind)
│   ├── src/
│   │   ├── components/         # PromptInput, ResultView, MermaidDiagram, Section
│   │   ├── api/                # API client
│   │   └── App.tsx, main.tsx
│   ├── package.json
│   └── vite.config.ts
├── system_design_mcp/
│   ├── agents/                 # Requirement, Architecture, Infra, API, Workflow, Diagram, Formatter
│   ├── core/                    # config, mcp_controller
│   ├── models/                  # Pydantic schemas
│   ├── utils/                   # logger, llm_client, mermaid_renderer, load_estimation
│   └── api/
│       └── main.py              # FastAPI app (CORS, optional static serve of web/dist)
```

## Requirements

- **Backend**: Python 3.11+, API key (OpenAI / Azure OpenAI) or Ollama
- **Frontend**: Node.js 18+ and npm (for the React app)

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
   # - LLM_PROVIDER=openai | azure | ollama
   # - Azure: AZURE_ENDPOINT, AZURE_KEY (or AZURE_API_KEY), AZURE_API_VERSION, AZURE_DEPLOYMENT
   # - OpenAI: OPENAI_API_KEY=sk-..., OPENAI_MODEL=gpt-4o
   # - Ollama: OLLAMA_BASE_URL=http://localhost:11434, OLLAMA_MODEL=llama3.2
   ```

## Run Locally

### 1. Backend (API)

```bash
source .venv/bin/activate
uvicorn system_design_mcp.api.main:app --host 0.0.0.0 --port 8000
```

Or from repo root: `./run_api.sh`

### 2. Frontend (React)

In a **second terminal**:

```bash
cd web && npm install && npm run dev
```

Or from repo root: `./run_web.sh` (after `cd web && npm install` once).

Open **http://localhost:3000**. Enter a prompt (e.g. *"Design a scalable chat system like WhatsApp"*), click **Generate Design**, and view requirements, architecture, infrastructure, API, Mermaid diagrams, and scaling strategy. Use **Export Markdown** to download.

The Vite dev server proxies `/v1` and `/health` to the API on port 8000, so both must be running.

### Single-server (production-style)

Build the frontend and run FastAPI; it will serve the built app and the API:

```bash
cd web && npm run build && cd ..
uvicorn system_design_mcp.api.main:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** for the UI; **http://localhost:8000/v1/design** for the API.

## Docker

Build the frontend first, then the Docker image (see Dockerfile). For a quick API-only run:

```bash
docker build -t system-design-mcp .
docker run -p 8000:8000 --env-file .env system-design-mcp \
  uvicorn system_design_mcp.api.main:app --host 0.0.0.0 --port 8000
```

To serve the React app from Docker, build the web app into `web/dist` before `docker build`, and use a CMD that runs uvicorn (so the app serves both API and static frontend at port 8000).

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `openai`, `azure`, or `ollama` | `openai` |
| `AZURE_ENDPOINT` | Azure OpenAI base URL (e.g. `https://xxx.openai.azure.com`) | - |
| `AZURE_KEY` or `AZURE_API_KEY` | Azure OpenAI API key | - |
| `AZURE_API_VERSION` | Azure API version | `2025-01-01-preview` |
| `AZURE_DEPLOYMENT` | Azure deployment name | `gpt-4o` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.2` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_HOST` / `API_PORT` | FastAPI host/port | `0.0.0.0` / `8000` |

## Export

- **Markdown**: Use **Export Markdown** in the web UI to download a single `.md` file with all sections and Mermaid code blocks.
- **JSON**: Use **POST /v1/design**; the response is full JSON (overview, requirements, components, infrastructure, API, Mermaid strings, scaling strategy).

## Optional: Load Estimation

The codebase is structured so you can add a **load estimation** module (e.g. in `utils/` or a dedicated agent) that estimates QPS, storage, and bandwidth from requirements and scale assumptions, and inject it into the formatter or API response.

## License

MIT.
