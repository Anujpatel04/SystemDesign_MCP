# System Design MCP Agent Platform - Production Dockerfile
# Python 3.11+ multi-stage build

FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH"

# Install runtime deps only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY . .
RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "system_design_mcp.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
