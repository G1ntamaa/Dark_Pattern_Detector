import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from detector import DarkPatternAnalyzer, PATTERNS
from scraper import scrape_page, DEMO_SAMPLES

#  Page Config
st.set_page_config(
    page_title="Dark Pattern Detector",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

#  Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    .main { background-color: #0d0d0d; }
    .stApp { background-color: #0d0d0d; color: #f0f0f0; }

    .score-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #333;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 16px;
    }
    .score-number {
        font-size: 72px;
        font-weight: 700;
        font-family: 'IBM Plex Mono', monospace;
        line-height: 1;
    }
    .detection-card {
        background: #1a1a1a;
        border-left: 4px solid;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        color: #888;
        font-size: 1.05rem;
        margin-top: 4px;
        margin-bottom: 32px;
    }
    div[data-testid="stMetric"] {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 16px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 15px;
        padding: 12px 32px;
        width: 100%;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    .stTextArea textarea {
        background: #1a1a1a !important;
        color: #f0f0f0 !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 13px !important;
    }
    .stTextInput input {
        background: #1a1a1a !important;
        color: #f0f0f0 !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
    }
    .sidebar .sidebar-content { background: #111; }
    hr { border-color: #2a2a2a; }
    .pattern-legend {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 0;
        border-bottom: 1px solid #222;
    }
    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }
</style>
""", unsafe_allow_html=True)

#  Initialize
@st.cache_resource
def load_analyzer():
    return DarkPatternAnalyzer()

analyzer = load_analyzer()

#  Sidebar
with st.sidebar:
    st.markdown("## 🕵️ Dark Pattern Detector")
    st.markdown("*Exposing deceptive UX in e-commerce*")
    st.markdown("---")

    st.markdown("### 📚 Pattern Reference")
    for name, config in PATTERNS.items():
        severity_color = {"High": "#FF4444", "Medium": "#FF8C00", "Low": "#3498DB"}.get(config["severity"], "#888")
        st.markdown(
            f"""<div class='pattern-legend'>
                <div class='dot' style='background:{config["color"]}'></div>
                <div>
                    <strong style='font-size:13px'>{config['icon']} {name}</strong><br>
                    <span style='font-size:11px;color:#888'>{config['description'][:55]}...</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This tool uses a **hybrid ML + rule-based engine** to detect 8 categories of dark patterns 
    used by e-commerce platforms to manipulate consumer behaviour.
    
    **Tech Stack:** Python · Scikit-learn · NLP · BeautifulSoup · Streamlit · Plotly
    
    Built by [Sahil Rai](mailto:raisahil909@gmail.com)
    """)

#  Hero Header
st.markdown('<p class="hero-title">Dark Pattern Detector</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyze e-commerce pages for deceptive UX patterns using ML + NLP</p>', unsafe_allow_html=True)

#  Input Section
tab1, tab2, tab3 = st.tabs(["🔗 Analyze URL", "📋 Paste Text", "🧪 Try Demo"])

with tab1:
    st.markdown("#### Enter a product page URL")
    url_input = st.text_input(
        "URL",
        placeholder="https://www.amazon.in/dp/...",
        label_visibility="collapsed"
    )
    col1, col2 = st.columns([1, 3])
    with col1:
        analyze_url = st.button("🔍 Analyze URL", key="url_btn")

    if analyze_url and url_input:
        with st.spinner("Fetching page..."):
            text, title, success = scrape_page(url_input)
        if not success:
            st.error(f"Could not fetch page: {title}\n\n💡 Try pasting the page text in the 'Paste Text' tab instead.")
        elif text:
            with st.spinner("Detecting dark patterns..."):
                result = analyzer.analyze_text(text, url=url_input, title=title)
            st.session_state["result"] = result
        else:
            st.warning("Page was fetched but no content was extracted. Try pasting the text manually.")

with tab2:
    st.markdown("#### Paste product page text")
    text_input = st.text_area(
        "Page content",
        placeholder="Paste the product listing text here — descriptions, pricing, badges, buttons, all of it...",
        height=200,
        label_visibility="collapsed"
    )
    col1, col2 = st.columns([1, 3])
    with col1:
        analyze_text = st.button("🔍 Analyze Text", key="text_btn")

    if analyze_text and text_input:
        with st.spinner("Detecting dark patterns..."):
            result = analyzer.analyze_text(text_input, url="Manual Input", title="Pasted Content")
        st.session_state["result"] = result

with tab3:
    st.markdown("#### Choose a demo sample")
    demo_choice = st.selectbox("Demo", list(DEMO_SAMPLES.keys()), label_visibility="collapsed")
    st.code(DEMO_SAMPLES[demo_choice][:400] + "...", language=None)
    col1, col2 = st.columns([1, 3])
    with col1:
        run_demo = st.button("▶ Run Demo", key="demo_btn")

    if run_demo:
        with st.spinner("Analyzing demo..."):
            demo_text = DEMO_SAMPLES[demo_choice]
            result = analyzer.analyze_text(demo_text, url="Demo", title=demo_choice)
        st.session_state["result"] = result

#  Results
if "result" in st.session_state:
    result = st.session_state["result"]
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    st.markdown(f"**Page:** `{result.page_title}`")

    # Top KPI row
    c1, c2, c3, c4 = st.columns(4)
    score_color = "#2ecc71" if result.score == 0 else "#f39c12" if result.score <= 30 else "#e74c3c"
    c1.markdown(
        f"""<div class='score-card'>
            <div class='score-number' style='color:{score_color}'>{result.score}</div>
            <div style='color:#888;margin-top:8px;font-size:14px'>Deception Score /100</div>
            <div style='font-size:22px;margin-top:6px'>{result.verdict}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    c2.metric("🚨 Patterns Found", len(result.detections))
    c3.metric("📂 Categories", len(result.category_counts))
    high_count = sum(1 for d in result.detections if d.severity == "High")
    c4.metric("🔴 High Severity", high_count)

    if not result.detections:
        st.success("🎉 No dark patterns detected! This looks like a clean product listing.")
    else:
        st.markdown("---")
        col_left, col_right = st.columns([1, 1])

        # ── Bar chart ──
        with col_left:
            st.markdown("### Pattern Breakdown")
            df_chart = pd.DataFrame(
                [(k, v, PATTERNS.get(k, {}).get("color", "#888")) for k, v in result.category_counts.items()],
                columns=["Pattern", "Count", "Color"]
            ).sort_values("Count", ascending=True)

            fig = go.Figure(go.Bar(
                x=df_chart["Count"],
                y=df_chart["Pattern"],
                orientation="h",
                marker_color=df_chart["Color"],
                text=df_chart["Count"],
                textposition="outside",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#f0f0f0",
                margin=dict(l=10, r=40, t=20, b=10),
                height=320,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── Severity donut ──
        with col_right:
            st.markdown("### Severity Distribution")
            sev_counts = {"High": 0, "Medium": 0, "Low": 0}
            for d in result.detections:
                sev_counts[d.severity] = sev_counts.get(d.severity, 0) + 1

            fig2 = go.Figure(go.Pie(
                labels=list(sev_counts.keys()),
                values=list(sev_counts.values()),
                hole=0.55,
                marker_colors=["#FF4444", "#FF8C00", "#3498DB"],
                textfont_size=13,
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#f0f0f0",
                margin=dict(l=10, r=10, t=20, b=10),
                height=320,
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(text=f"<b>{len(result.detections)}</b><br>found", x=0.5, y=0.5,
                                  font_size=16, font_color="#f0f0f0", showarrow=False)],
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── Detection cards ──
        st.markdown("### 🔎 Detected Instances")

        filter_options = ["All"] + list(result.category_counts.keys())
        selected_filter = st.selectbox("Filter by category", filter_options)

        shown = result.detections if selected_filter == "All" else [
            d for d in result.detections if d.pattern_type == selected_filter
        ]

        for d in shown:
            sev_bg = {"High": "#3d0000", "Medium": "#2d1a00", "Low": "#001a2d"}.get(d.severity, "#1a1a1a")
            st.markdown(
                f"""<div class='detection-card' style='border-color:{d.color};background:{sev_bg}'>
                    <div style='display:flex;justify-content:space-between;align-items:center'>
                        <span style='font-weight:700;color:{d.color}'>{d.icon} {d.pattern_type}</span>
                        <span class='badge' style='background:{d.color}22;color:{d.color}'>{d.severity}</span>
                    </div>
                    <div style='font-family:IBM Plex Mono,monospace;font-size:13px;color:#ddd;margin-top:8px'>
                        "{d.matched_text}"
                    </div>
                    <div style='font-size:12px;color:#666;margin-top:4px'>Context: {d.context}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # ── Export CSV ──
        st.markdown("---")
        df_export = analyzer.get_summary_df(result)
        if not df_export.empty:
            csv = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️  Export Report as CSV",
                data=csv,
                file_name="dark_pattern_report.csv",
                mime="text/csv",
            )
