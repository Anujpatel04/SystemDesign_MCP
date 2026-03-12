"""
Structured logging for the System Design MCP platform.

Uses structlog when available, otherwise falls back to standard logging.
"""

import logging
import sys
from typing import Any

from system_design_mcp.core.config import get_settings

try:
    import structlog
    from structlog.types import Processor
    _HAS_STRUCTLOG = True
except ImportError:
    _HAS_STRUCTLOG = False


def _configure_processors() -> list[Any]:
    """Build list of structlog processors."""
    if not _HAS_STRUCTLOG:
        return []
    shared: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.dev.set_exc_info,
    ]
    if sys.stderr.isatty():
        shared.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        shared.append(structlog.processors.JSONRenderer())
    return shared


class _FallbackLogger:
    """Minimal logger when structlog is not installed."""

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger(name)

    def info(self, msg: str, **kwargs: Any) -> None:
        extra = " ".join(f"{k}={v}" for k, v in kwargs.items())
        self._log.info("%s %s", msg, extra)

    def error(self, msg: str, **kwargs: Any) -> None:
        extra = " ".join(f"{k}={v}" for k, v in kwargs.items())
        self._log.error("%s %s", msg, extra)

    def exception(self, msg: str, **kwargs: Any) -> None:
        self._log.exception(msg, extra=kwargs)


def get_logger(name: str) -> Any:
    """Return a configured bound logger for the given module name."""
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
        level=level,
    )
    if _HAS_STRUCTLOG:
        structlog.configure(
            processors=_configure_processors(),
            wrapper_class=structlog.make_filtering_bound_logger(level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger(name)
    return _FallbackLogger(name)


def log_agent_start(logger: Any, agent: str, prompt_preview: str = "") -> None:
    """Log the start of an agent run."""
    preview = prompt_preview[:100] + "..." if len(prompt_preview) > 100 else prompt_preview
    logger.info("agent_start", agent=agent, prompt_preview=preview)


def log_agent_end(logger: Any, agent: str, success: bool = True, error: str | None = None) -> None:
    """Log the end of an agent run."""
    logger.info("agent_end", agent=agent, success=success, error=error)
