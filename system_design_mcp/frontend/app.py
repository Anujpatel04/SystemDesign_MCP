"""
Streamlit UI for the System Design MCP Agent Platform.

Allows users to enter a system design prompt and view generated
requirements, architecture, infrastructure, API, diagrams, and scaling strategy.
"""

import asyncio
import sys
from pathlib import Path

import streamlit as st

# Add project root for imports
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_design_mcp.core.mcp_controller import MCPController
from system_design_mcp.models.schemas import FormattedOutput
from system_design_mcp.utils.mermaid_renderer import render_mermaid_safe


def format_output_as_markdown(output: FormattedOutput) -> str:
    """Build a single Markdown string from FormattedOutput for export."""
    lines = [
        "# System Design Output",
        "",
        "## System Overview",
        output.system_overview or "",
        "",
        "## Functional Requirements",
        *([f"- {r}" for r in (output.functional_requirements or [])]),
        "",
        "## Non-Functional Requirements",
        *([f"- {r}" for r in (output.non_functional_requirements or [])]),
        "",
        "## Architecture Components",
        *([f"- **{c.name}**: {c.description}" for c in (output.architecture_components or [])]),
        "",
        "## Infrastructure",
        *([f"- **{i.name}** ({i.category}): {i.description}" for i in (output.infrastructure_stack or [])]),
        "",
        "## API Endpoints",
        *([f"- `{e.method} {e.path}`: {e.description}" for e in (output.api_design or [])]),
        "",
        "## Architecture Diagram",
        "```mermaid",
        output.architecture_diagram_mermaid or "",
        "```",
        "",
        "## Workflow Diagram",
        "```mermaid",
        output.workflow_diagram_mermaid or "",
        "```",
        "",
        "## Scaling Strategy",
        *([f"- {s}" for s in (output.scaling_strategy or [])]),
    ]
    return "\n".join(lines)


# Page config
st.set_page_config(
    page_title="System Design MCP",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a more polished UI
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2d5a87;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid #4a90d9;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2d5a87 0%, #4a90d9 100%);
        color: white;
    }
    .mermaid-container {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def render_mermaid(mermaid_code: str, height: int = 400) -> None:
    """Render Mermaid diagram in Streamlit using Mermaid.js CDN."""
    safe = render_mermaid_safe(mermaid_code)
    if not safe:
        st.code(mermaid_code, language="mermaid")
        return
    html = f"""
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    <div class="mermaid">
    {safe}
    </div>
    """
    # Use st.components.v1.html with the full Mermaid ES module approach
    # Mermaid 10+ requires ES modules; use a simpler script that loads UMD for compatibility
    html_umd = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"></script>
    <div class="mermaid" style="text-align: center;">
    {safe}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    """
    st.components.v1.html(html_umd, height=height, scrolling=False)


def render_result(output: FormattedOutput) -> None:
    """Render the formatted system design output in the UI."""
    st.markdown('<p class="main-header">🏗️ System Design Result</p>', unsafe_allow_html=True)

    st.markdown("### 1. System Overview")
    st.write(output.system_overview or "_No overview generated._")

    st.markdown('<p class="section-header">2. Functional Requirements</p>', unsafe_allow_html=True)
    for req in output.functional_requirements or []:
        st.markdown(f"- {req}")
    if not output.functional_requirements:
        st.write("_None listed._")

    st.markdown('<p class="section-header">3. Non-Functional Requirements</p>', unsafe_allow_html=True)
    for req in output.non_functional_requirements or []:
        st.markdown(f"- {req}")
    if not output.non_functional_requirements:
        st.write("_None listed._")

    st.markdown('<p class="section-header">4. Architecture Components</p>', unsafe_allow_html=True)
    for comp in output.architecture_components or []:
        with st.expander(f"**{comp.name}**"):
            st.write(comp.description)
            for r in comp.responsibilities or []:
                st.markdown(f"- {r}")
    if not output.architecture_components:
        st.write("_None listed._")

    st.markdown('<p class="section-header">5. Infrastructure Stack</p>', unsafe_allow_html=True)
    if output.infrastructure_stack:
        for item in output.infrastructure_stack:
            st.markdown(f"- **{item.name}** ({item.category}): {item.description}")
            if item.use_case:
                st.caption(f"  Use case: {item.use_case}")
    else:
        st.write("_None listed._")

    st.markdown('<p class="section-header">6. API Endpoints</p>', unsafe_allow_html=True)
    if output.api_design:
        for ep in output.api_design:
            st.markdown(f"**`{ep.method} {ep.path}`** — {ep.description}")
            if ep.request_fields:
                with st.expander("Request fields"):
                    st.json(ep.request_fields)
            if ep.response_structure:
                with st.expander("Response structure"):
                    st.json(ep.response_structure) if isinstance(ep.response_structure, (dict, list)) else st.write(ep.response_structure)
    else:
        st.write("_None listed._")

    st.markdown('<p class="section-header">7. Architecture Diagram</p>', unsafe_allow_html=True)
    if output.architecture_diagram_mermaid:
        render_mermaid(output.architecture_diagram_mermaid, height=450)
    else:
        st.info("No architecture diagram was generated.")

    st.markdown('<p class="section-header">8. Workflow Diagram</p>', unsafe_allow_html=True)
    if output.workflow_diagram_mermaid:
        render_mermaid(output.workflow_diagram_mermaid, height=400)
    else:
        st.info("No workflow diagram was generated.")

    st.markdown('<p class="section-header">9. Scaling Strategy</p>', unsafe_allow_html=True)
    for s in output.scaling_strategy or []:
        st.markdown(f"- {s}")
    if not output.scaling_strategy:
        st.write("_None listed._")


def main() -> None:
    st.markdown('<p class="main-header">🏗️ System Design MCP Agent Platform</p>', unsafe_allow_html=True)
    st.markdown("Generate distributed system architecture, APIs, and diagrams from a natural language prompt.")

    prompt = st.text_area(
        "System design prompt",
        height=120,
        placeholder="e.g. Design a scalable ride sharing system like Uber",
        help="Describe the system you want to design.",
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        generate = st.button("Generate Design", type="primary", use_container_width=True)
    with col2:
        if "last_result" in st.session_state:
            md = format_output_as_markdown(st.session_state["last_result"])
            st.download_button("Download Markdown", md, file_name="system_design.md", mime="text/markdown", use_container_width=True, key="download_md")

    if generate and prompt and prompt.strip():
        with st.spinner("Generating system design (this may take a minute)..."):
            try:
                controller = MCPController()
                result = asyncio.run(controller.run(prompt.strip()))
                st.session_state["last_result"] = result
                st.session_state["last_prompt"] = prompt.strip()
                render_result(result)
            except Exception as e:
                st.error(f"Generation failed: {e}")
                st.exception(e)
    elif generate and not (prompt and prompt.strip()):
        st.warning("Please enter a system design prompt.")
    elif "last_result" in st.session_state:
        render_result(st.session_state["last_result"])

if __name__ == "__main__":
    main()
