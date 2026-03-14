"""
Streamlit demo for the AI Financial Analyst Agent.

Run from project root: streamlit run ui/streamlit_app.py
"""

import re
import sys
from pathlib import Path

# Add project root so "agent" and "tools" resolve when running: streamlit run ui/streamlit_app.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from agent.graph import create_financial_agent, run_analysis


def parse_report_sections(report: str) -> dict[str, str]:
    """Split report text into sections by ## Header. Returns dict of section_name -> content."""
    section_names = [
        "Asset/Summary",
        "Key Metrics",
        "Recent News",
        "Opportunities",
        "Risks",
    ]
    # Match ## Section Name at start of line
    pattern = re.compile(
        r"^##\s*(Asset/Summary|Key Metrics|Recent News|Opportunities|Risks)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    sections = {name: "" for name in section_names}
    matches = list(pattern.finditer(report))
    if not matches:
        return {"_raw": report}
    for i, m in enumerate(matches):
        header = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(report)
        content = report[start:end].strip()
        for name in section_names:
            if name.lower() == header.lower():
                sections[name] = content
                break
    if not any(sections.values()):
        return {"_raw": report}
    return sections


st.set_page_config(page_title="AI Financial Analyst", page_icon="📊", layout="wide")
st.title("📊 AI Financial Analyst Agent")
st.caption("Analyze stocks or crypto using real-time data and news. Powered by OpenAI, LangChain, and LangGraph.")

# Two main vertical columns: left = queries (~21% after -20% reduction), right = results
left_col, right_col = st.columns([3, 11], gap="medium")

with left_col:
    # Left column: #e5e5e5 background, query input with white background
    st.markdown(
        '<span id="query-column-marker"></span>'
        '<style>'
        'div[data-testid="column"]:has(#query-column-marker) { '
        '  background-color: #e5e5e5; padding: 1.25rem; border-radius: 0.5rem; '
        '  min-height: 80vh; '
        '}'
        'div[data-testid="column"]:has(#query-column-marker) textarea { '
        '  background-color: #ffffff !important; '
        '}'
        '</style>',
        unsafe_allow_html=True,
    )
    st.subheader("Query")
    query = st.text_area(
        "Your request",
        height=180,
        placeholder="e.g. Analyze Tesla stock and summarize opportunities and risks.",
        label_visibility="collapsed",
        key="query_input",
    )
    run = st.button("Run analysis", type="primary", use_container_width=True)
    st.markdown("**Example queries:**")
    st.markdown("- Analyze Tesla stock.")
    st.markdown("- Analyze Nvidia stock and summarize risks.")
    st.markdown("- Analyze Bitcoin price trends.")
    st.markdown("- Compare Apple and Microsoft financial metrics.")

with right_col:
    st.subheader("Results")
    # Use session state to keep last report when layout re-runs
    if "last_report" not in st.session_state:
        st.session_state.last_report = None
    if "last_query" not in st.session_state:
        st.session_state.last_query = None

    if run and query.strip():
        with st.spinner("Running agent (fetching data and generating report)…"):
            try:
                report = run_analysis(query.strip())
                st.session_state.last_report = report
                st.session_state.last_query = query.strip()
            except Exception as e:
                st.error(f"Error: {e}")
                st.code(str(e))
                report = None
    elif run and not query.strip():
        report = None  # show warning, not previous result
    else:
        report = st.session_state.last_report

    if report:
        sections = parse_report_sections(report)
        if "_raw" in sections:
            st.markdown(sections["_raw"])
        else:
            # Three result columns: 1st ~20% narrower, 2nd and 3rd get more space
            c1, c2, c3 = st.columns([8, 11, 11], gap="medium")
            with c1:
                st.markdown("#### Asset / Summary")
                st.markdown(sections.get("Asset/Summary") or "*—*")
                st.markdown("---")
                st.markdown("#### Key Metrics")
                st.markdown(sections.get("Key Metrics") or "*—*")
            with c2:
                st.markdown("#### Recent News")
                st.markdown(sections.get("Recent News") or "*—*")
            with c3:
                st.markdown("#### Opportunities")
                st.markdown(sections.get("Opportunities") or "*—*")
                st.markdown("---")
                st.markdown("#### Risks")
                st.markdown(sections.get("Risks") or "*—*")
    elif not run:
        st.info("Enter a query and click **Run analysis** to see results here.")
    elif run and not query.strip():
        st.warning("Please enter a query.")
