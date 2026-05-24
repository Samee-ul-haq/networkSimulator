"""
Network Simulator — Streamlit UI
=================================
Usage (run from inside the netsim / backend folder):

    pip install streamlit
    streamlit run app.py
"""

import io
import sys
from contextlib import redirect_stdout

import streamlit as st

# ── Make sure the local packages are importable ───────────────────────────
sys.path.insert(0, ".")

# ══════════════════════════════════════════════════════════════════════════
#  Page config  (must be first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Network Simulator · ITT351",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════
#  Global CSS
# ══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* Larger sidebar */
[data-testid="stSidebar"] { min-width: 270px; }
/* Tighten sidebar buttons */
[data-testid="stSidebar"] .stButton button {
    font-size: 12px;
    padding: 4px 8px;
    text-align: left;
}
/* Output pre block */
.sim-output {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px 20px;
    overflow-x: auto;
    overflow-y: auto;
    max-height: 72vh;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 12.5px;
    line-height: 1.55;
    white-space: pre;
}
/* Metric tweaks */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px 14px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  Load test functions (once per session)
# ══════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Loading simulator …")
def _load():
    from main import (
        test_s1_p2p, test_s1_hub_star, test_s1_switch, test_s1_two_stars,
        test_s2_arp_static_routing, test_s2_rip,
        test_s3_chat, test_s3_file_transfer,
        test_s3_gobackn_detailed, test_s3_full_stack_encapsulation,
    )
    return {
        "S1-TC1": ("P2P Direct Link",               "1", test_s1_p2p),
        "S1-TC2": ("Hub Star  (5 devices)",          "1", test_s1_hub_star),
        "S1-TC3": ("Switch — MAC Learning",          "1", test_s1_switch),
        "S1-TC4": ("Two Hub-Stars via Switch",       "1", test_s1_two_stars),
        "S2-TC1": ("Dynamic ARP + Static Routing",   "2", test_s2_arp_static_routing),
        "S2-TC2": ("RIP Dynamic Routing",            "2", test_s2_rip),
        "S3-TC1": ("Chat App — Full Stack",          "3", test_s3_chat),
        "S3-TC2": ("File Transfer + Go-Back-N",      "3", test_s3_file_transfer),
        "S3-TC3": ("Go-Back-N Detail  (8 segs)",     "3", test_s3_gobackn_detailed),
        "S3-TC4": ("Full Encapsulation Demo",        "3", test_s3_full_stack_encapsulation),
    }

TESTS = _load()


# ══════════════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════════════

def run_test(func) -> str:
    """Capture everything printed by *func* and return it as a string."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            func()
        except Exception as exc:
            import traceback
            print(f"\n[ERROR] {type(exc).__name__}: {exc}")
            traceback.print_exc(file=buf)
    return buf.getvalue()


# Layer-based colour map for syntax highlighting
_COLOURS = {
    "[PHYSICAL]" : "#4fc3f7",   # blue
    "bit signal" : "#4fc3f7",
    "bits prop"  : "#4fc3f7",
    "[HUB"       : "#80deea",
    "[SWITCH"    : "#80cbc4",
    "[CSMA"      : "#80deea",
    "CSMA/CD"    : "#80deea",
    "[DATA LINK]": "#81c784",   # green
    "DATA LINK"  : "#81c784",
    "[DL]"       : "#81c784",
    "FCS"        : "#81c784",
    "MAC"        : "#81c784",
    "[ARP]"      : "#4db6ac",   # teal
    "ARP"        : "#4db6ac",
    "[NETWORK"   : "#ffb74d",   # orange
    "NETWORK"    : "#ffb74d",
    "[NET]"      : "#ffb74d",
    "TTL"        : "#ffb74d",
    "[RIP]"      : "#ff8a65",   # deep orange
    "RIP"        : "#ff8a65",
    "[ROUTER"    : "#ffa726",
    "ROUTER"     : "#ffa726",
    "[TRANSPORT" : "#ce93d8",   # purple
    "TRANSPORT"  : "#ce93d8",
    "[GBN"       : "#fff176",   # yellow
    "GBN"        : "#fff176",
    "[APP]"      : "#f48fb1",   # pink
    "APPLICATION": "#f48fb1",
    "APP]"       : "#f48fb1",
    "[FTP]"      : "#ffcc80",   # amber
    "FTP"        : "#ffcc80",
    "[CHAT"      : "#f06292",
    "CHAT"       : "#f06292",
    "✓"          : "#69f0ae",   # green tick
    "✗"          : "#ff5252",   # red cross
    "ERROR"      : "#ff5252",
    "═"          : "#444c56",   # dim separators
    "╔"          : "#444c56",
    "╚"          : "#444c56",
    "┌"          : "#555",
    "│"          : "#555",
    "└"          : "#555",
    "├"          : "#555",
}


def _html_line(line: str) -> str:
    safe = (line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))
    colour = "#c9d1d9"          # default: GitHub-dark text
    for key, col in _COLOURS.items():
        if key in line:
            colour = col
            break
    return f'<span style="color:{colour}">{safe}</span>'


def render_output(text: str):
    """Render simulator output with layer-based colour coding."""
    html_lines = [_html_line(ln) for ln in text.split("\n")]
    html = "\n".join(html_lines)
    st.markdown(
        f'<div class="sim-output">{html}</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════
#  Session state
# ══════════════════════════════════════════════════════════════════════════

if "outputs"   not in st.session_state:
    st.session_state.outputs   = {}    # tc_id → output string
if "active_tc" not in st.session_state:
    st.session_state.active_tc = None


# ══════════════════════════════════════════════════════════════════════════
#  Sidebar
# ══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🌐 Network Simulator")
    st.caption("NIT Srinagar · ITT351")
    st.divider()

    # ── Run All ───────────────────────────────────────────────────────────
    if st.button("▶▶  Run All Test Cases", type="primary", use_container_width=True):
        combined = ""
        bar = st.progress(0)
        total = len(TESTS)
        for i, (tc_id, (name, sub, func)) in enumerate(TESTS.items()):
            bar.progress(i / total, text=f"Running {tc_id} …")
            out = run_test(func)
            st.session_state.outputs[tc_id] = out
            combined += f"\n{'═'*64}\n  {tc_id} · {name}\n{'═'*64}\n{out}"
        st.session_state.outputs["ALL"] = combined
        st.session_state.active_tc      = "ALL"
        bar.progress(1.0, text="All done ✓")

    # ── Clear ─────────────────────────────────────────────────────────────
    if st.button("🗑  Clear outputs", use_container_width=True):
        st.session_state.outputs.clear()
        st.session_state.active_tc = None
        st.rerun()

    st.divider()

    # ── Individual test cases grouped by submission ───────────────────────
    for sub_label, sub_id in [
        ("Submission 1 · Physical & Data Link", "1"),
        ("Submission 2 · Network Layer",        "2"),
        ("Submission 3 · Transport & App",      "3"),
    ]:
        st.markdown(f"**{sub_label}**")
        for tc_id, (name, sub, func) in TESTS.items():
            if sub != sub_id:
                continue
            ran   = tc_id in st.session_state.outputs
            label = f"{'✓ ' if ran else ''}{tc_id}: {name}"
            if st.button(label, key=f"btn_{tc_id}", use_container_width=True):
                with st.spinner(f"Running {tc_id} …"):
                    st.session_state.outputs[tc_id] = run_test(func)
                st.session_state.active_tc = tc_id
                st.rerun()
        st.divider()


# ══════════════════════════════════════════════════════════════════════════
#  Main area
# ══════════════════════════════════════════════════════════════════════════

if st.session_state.active_tc is None:
    # ── Welcome screen ────────────────────────────────────────────────────
    st.title("Network Simulator")
    st.markdown("### Complete Protocol Stack — Submissions 1 · 2 · 3")

    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown("#### Protocol Stack")
        st.markdown("""
| Layer | Protocol | Key Features |
|---|---|---|
| **Application** | Chat · File Transfer | Ports 5000, 5010 |
| **Transport** | TCP + Go-Back-N | Checksum · Sliding window |
| **Network** | IPv4 + RIP | LPM · Bellman-Ford |
| **Data Link** | Ethernet + ARP | CRC-32 FCS · Dynamic ARP |
| **Physical** | P2P / Hub / Switch | CSMA/CD · MAC learning |
""")

    with col_r:
        st.markdown("#### Test Cases")
        st.markdown("""
| ID | Description | Sub |
|---|---|:---:|
| S1-TC1 | P2P Direct Link | 1 |
| S1-TC2 | Hub Star Topology | 1 |
| S1-TC3 | Switch — MAC Learning | 1 |
| S1-TC4 | Two Hub-Stars via Switch | 1 |
| S2-TC1 | Dynamic ARP + Static Routing | 2 |
| S2-TC2 | RIP Convergence | 2 |
| S3-TC1 | Chat App — Full Stack | 3 |
| S3-TC2 | File Transfer + Go-Back-N | 3 |
| S3-TC3 | Go-Back-N Detail | 3 |
| S3-TC4 | Full Encapsulation Demo | 3 |
""")

    st.info("👈  Select a test case from the sidebar, or click **Run All**.")

else:
    # ── Output view ───────────────────────────────────────────────────────
    active = st.session_state.active_tc
    output = st.session_state.outputs.get(active, "")

    if active == "ALL":
        title = "All Test Cases"
    else:
        name, _, _ = TESTS[active]
        title = f"{active} · {name}"

    st.markdown(f"### {title}")

    # ── Stats strip ───────────────────────────────────────────────────────
    lines_n  = output.count("\n")
    checks   = output.count("✓")
    losses   = output.count("✗")
    bits_n   = sum(
        int(tok.replace("-bit", ""))
        for tok in output.split()
        if tok.endswith("-bit") and tok.split("-")[0].isdigit()
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Output lines",       lines_n)
    c2.metric("Checks passed ✓",    checks)
    c3.metric("Simulated losses ✗", losses)
    c4.metric("Bits transmitted",   f"{bits_n:,}")

    st.markdown("---")

    # ── Coloured output ───────────────────────────────────────────────────
    render_output(output)

    # ── Download ──────────────────────────────────────────────────────────
    st.markdown("")
    st.download_button(
        label    = "⬇  Download output (.txt)",
        data     = output,
        file_name= f"{active}_output.txt",
        mime     = "text/plain",
    )
