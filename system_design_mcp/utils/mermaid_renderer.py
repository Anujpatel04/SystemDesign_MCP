"""
Mermaid diagram rendering utilities.

Provides safe extraction and validation of Mermaid code blocks
for rendering in the Streamlit frontend.
"""

import re
from typing import Literal

# Mermaid block pattern: ```mermaid ... ``` or ``` ... ``` with flowchart/sequenceDiagram
MERMAID_BLOCK_RE = re.compile(
    r"```(?:mermaid)?\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def extract_mermaid(code: str, diagram_type: Literal["flowchart", "sequence", "any"] = "any") -> str:
    """
    Extract the first Mermaid code block from a string.
    If diagram_type is 'flowchart', only return content that starts with flowchart.
    If 'sequence', only content that starts with sequenceDiagram.
    """
    if not code or not code.strip():
        return ""
    matches = MERMAID_BLOCK_RE.findall(code)
    for m in matches:
        block = m.strip()
        if not block:
            continue
        if diagram_type == "flowchart" and not (
            block.startswith("flowchart") or block.startswith("graph")
        ):
            continue
        if diagram_type == "sequence" and not block.startswith("sequenceDiagram"):
            continue
        return block
    # No code block: if the whole thing looks like mermaid, return as-is
    if diagram_type == "any" and (
        "flowchart" in code or "sequenceDiagram" in code or "graph " in code
    ):
        return code.strip()
    return ""


def render_mermaid_safe(mermaid_code: str) -> str:
    """
    Return sanitized Mermaid code safe for embedding in HTML/Streamlit.
    Strips script tags and dangerous patterns. Returns empty string if invalid.
    """
    if not mermaid_code or not mermaid_code.strip():
        return ""
    # Remove potential script injection
    safe = mermaid_code.strip()
    for bad in ("<script", "</script>", "javascript:", "onerror=", "onload="):
        if bad.lower() in safe.lower():
            return ""
    return safe
