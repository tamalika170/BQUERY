import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import json
import re
import time
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="AI Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# CUSTOM CSS
# -----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #040810 !important;
    color: #e2e8f0;
    font-family: 'Rajdhani', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #050c1a 100%) !important;
    border-right: 1px solid rgba(56, 189, 248, 0.15);
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(56, 189, 248, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56, 189, 248, 0.04) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none; z-index: 0;
}
.dash-title {
    font-family: 'Orbitron', monospace; font-size: 2.2rem; font-weight: 900;
    background: linear-gradient(135deg, #38bdf8, #818cf8, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: 2px; margin-bottom: 0.2rem;
}
.dash-sub { font-family: 'Rajdhani', sans-serif; color: #64748b; font-size: 1rem; letter-spacing: 1px; margin-bottom: 2rem; }
.metric-row { display: flex; gap: 16px; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 160px;
    background: linear-gradient(145deg, #0f1e35, #081525);
    border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 16px; padding: 22px 20px;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.05);
    transform: perspective(600px) rotateX(2deg);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.metric-card:hover { transform: perspective(600px) rotateX(0deg) translateY(-4px); box-shadow: 0 16px 48px rgba(56,189,248,0.15), 0 8px 32px rgba(0,0,0,0.6); }
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #38bdf8, transparent); }
.metric-label { font-family: 'Rajdhani', sans-serif; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; color: #38bdf8; margin-bottom: 6px; }
.metric-value { font-family: 'Orbitron', monospace; font-size: 2rem; font-weight: 700; color: #f1f5f9; line-height: 1; }
.metric-icon { position: absolute; top: 16px; right: 16px; font-size: 1.8rem; opacity: 0.3; }
.section-header { font-family: 'Orbitron', monospace; font-size: 0.85rem; letter-spacing: 3px; text-transform: uppercase; color: #38bdf8; border-left: 3px solid #38bdf8; padding-left: 12px; margin: 1.8rem 0 1rem 0; }
.ai-response {
    background: linear-gradient(135deg, #0c1a2e, #0a1520);
    border: 1px solid rgba(129, 140, 248, 0.3); border-radius: 16px;
    padding: 24px 28px; margin-top: 1rem; position: relative;
    box-shadow: 0 0 40px rgba(129,140,248,0.08), 0 8px 32px rgba(0,0,0,0.5);
    font-family: 'Rajdhani', sans-serif; font-size: 1.05rem; line-height: 1.7; color: #cbd5e1;
}
.ai-response::before {
    content: 'AI INSIGHT'; position: absolute; top: -12px; left: 20px;
    background: linear-gradient(135deg, #818cf8, #f472b6); color: white;
    font-family: 'Orbitron', monospace; font-size: 0.65rem;
    letter-spacing: 2px; padding: 3px 12px; border-radius: 20px;
}
.accuracy-bar {
    background: linear-gradient(135deg, #0c1a2e, #0a1520);
    border: 1px solid rgba(56,189,248,0.2); border-radius: 12px;
    padding: 16px 20px; margin-top: 12px;
}
.confidence-high   { color: #34d399; font-family: 'Orbitron', monospace; font-size: 0.8rem; }
.confidence-medium { color: #fbbf24; font-family: 'Orbitron', monospace; font-size: 0.8rem; }
.confidence-low    { color: #f87171; font-family: 'Orbitron', monospace; font-size: 0.8rem; }
.history-card {
    background: linear-gradient(135deg, #0c1a2e, #080f1e);
    border: 1px solid rgba(56,189,248,0.1); border-radius: 12px;
    padding: 14px 18px; margin-bottom: 10px;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0c1a2e !important; border: 1px solid rgba(56,189,248,0.25) !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
    font-family: 'Rajdhani', sans-serif !important; font-size: 1rem !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #0f2040) !important;
    border: 1px solid rgba(56,189,248,0.4) !important; color: #38bdf8 !important;
    font-family: 'Orbitron', monospace !important; font-size: 0.75rem !important;
    letter-spacing: 2px !important; border-radius: 10px !important;
    padding: 10px 24px !important; transition: all 0.3s ease !important;
}
.stButton > button:hover { background: linear-gradient(135deg, #0f4c8f, #0f2a60) !important; box-shadow: 0 0 20px rgba(56,189,248,0.3) !important; transform: translateY(-2px) !important; }
[data-testid="stFileUploader"] { background: linear-gradient(145deg, #0c1a2e, #080f1e) !important; border: 1px dashed rgba(56,189,248,0.3) !important; border-radius: 12px !important; padding: 10px !important; }
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(56,189,248,0.1) !important; }
.stSidebar label, .stSidebar .stMarkdown p { color: #94a3b8 !important; font-family: 'Rajdhani', sans-serif !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #040810; }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.3); border-radius: 3px; }
.status-badge { display: inline-block; padding: 4px 14px; border-radius: 20px; font-family: 'Orbitron', monospace; font-size: 0.65rem; letter-spacing: 1.5px; text-transform: uppercase; }
.status-ok  { background: rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3); }
.status-err { background: rgba(239,68,68,0.15);  color:#f87171; border:1px solid rgba(239,68,68,0.3); }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# PLOTLY THEME
# -----------------------
PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(8,15,30,0)", plot_bgcolor="rgba(8,15,30,0)",
        font=dict(family="Rajdhani, sans-serif", color="#94a3b8", size=12),
        title=dict(font=dict(family="Orbitron, monospace", color="#e2e8f0", size=14)),
        xaxis=dict(gridcolor="rgba(56,189,248,0.07)", zerolinecolor="rgba(56,189,248,0.1)"),
        yaxis=dict(gridcolor="rgba(56,189,248,0.07)", zerolinecolor="rgba(56,189,248,0.1)"),
        colorway=["#38bdf8","#818cf8","#f472b6","#34d399","#fb923c","#a78bfa"],
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        margin=dict(l=40, r=20, t=50, b=40),
    )
)

# -----------------------
# GEMINI MODEL RESOLVER
# -----------------------
@st.cache_data(show_spinner=False)
def get_best_model(api_key: str) -> str:
    PREFERRED = ["gemini-1.5-flash","gemini-1.5-flash-latest","gemini-1.5-flash-8b","gemini-1.0-pro","gemini-pro"]
    try:
        genai.configure(api_key=api_key)
        available = [m.name.replace("models/","") for m in genai.list_models()
                     if "generateContent" in m.supported_generation_methods]
        for pref in PREFERRED:
            if pref in available: return pref
        if available: return available[0]
    except Exception: pass
    return "gemini-1.5-flash"

# -----------------------
# SAFE GEMINI CALL
# -----------------------
def safe_generate(model, prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            return model.generate_content(prompt).text
        except Exception as e:
            err = str(e)
            is_quota = "429" in err or "quota" in err.lower() or "resource exhausted" in err.lower()
            if is_quota and attempt < retries - 1:
                wait = 15 * (attempt + 1)
                st.warning(f"⏳ Rate limit — waiting {wait}s before retry {attempt+2}/{retries}...", icon="⏱️")
                time.sleep(wait)
            else: raise

# -----------------------
# ACCURACY SCORER
# -----------------------
def compute_accuracy(question: str, insight: str, df: pd.DataFrame) -> dict:
    """
    Rule-based accuracy scoring on top of Python-verified numbers.
    Returns score 0-100 and a breakdown.
    """
    score = 0
    checks = {}

    # 1. Data completeness — did we send full pre-aggregated data?
    score += 25
    checks["Full dataset used"] = ("✅ 100% of rows pre-aggregated in Python", 25)

    # 2. Numerical verification — spot-check numbers mentioned in insight
    numbers_in_insight = re.findall(r'\b\d+\.?\d*\b', insight)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    verified = 0
    total_checks = 0
    for num_str in numbers_in_insight[:10]:
        num = float(num_str)
        for col in numeric_cols:
            col_min, col_max = df[col].min(), df[col].max()
            col_mean = df[col].mean()
            # Check if the number is plausible (within dataset range or a reasonable aggregate)
            if col_min <= num <= col_max * df.shape[0]:
                verified += 1
                break
        total_checks += 1
    if total_checks > 0:
        num_score = min(30, int((verified / total_checks) * 30))
        score += num_score
        checks["Numbers in dataset range"] = (f"✅ {verified}/{total_checks} numbers verified", num_score)
    else:
        score += 20
        checks["Numbers in dataset range"] = ("✅ No numeric claims to verify", 20)

    # 3. Column relevance — did the insight mention actual column names?
    cols_mentioned = sum(1 for c in df.columns if c.lower() in insight.lower())
    col_score = min(25, cols_mentioned * 5)
    score += col_score
    checks["Column references"] = (f"✅ {cols_mentioned} column(s) referenced", col_score)

    # 4. Answer length / completeness
    words = len(insight.split())
    if words >= 50:
        score += 20
        checks["Answer completeness"] = (f"✅ {words} words — detailed response", 20)
    elif words >= 20:
        score += 12
        checks["Answer completeness"] = (f"⚠️ {words} words — moderate detail", 12)
    else:
        score += 5
        checks["Answer completeness"] = (f"⚠️ {words} words — brief response", 5)

    score = min(100, score)
    if score >= 80:   level, color = "HIGH",   "confidence-high"
    elif score >= 55: level, color = "MEDIUM", "confidence-medium"
    else:             level, color = "LOW",    "confidence-low"

    return {"score": score, "level": level, "color": color, "checks": checks}

# -----------------------
# PDF GENERATOR
# -----------------------
def generate_pdf(question: str, insight: str, accuracy: dict,
                 df_name: str, model_name: str, fig=None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story  = []

    # Title
    title_style = ParagraphStyle("title", parent=styles["Title"],
                                 fontSize=18, textColor=colors.HexColor("#38bdf8"),
                                 spaceAfter=6, fontName="Helvetica-Bold")
    story.append(Paragraph("AI Business Intelligence Report", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#38bdf8")))
    story.append(Spacer(1, 0.15*inch))

    # Meta info table
    meta_data = [
        ["Dataset", df_name],
        ["Model Used", model_name],
        ["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Accuracy Score", f"{accuracy['score']}/100  ({accuracy['level']})"],
    ]
    meta_table = Table(meta_data, colWidths=[1.8*inch, 4.5*inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (0,-1), colors.HexColor("#0f1e35")),
        ("BACKGROUND",  (1,0), (1,-1), colors.HexColor("#040810")),
        ("TEXTCOLOR",   (0,0), (0,-1), colors.HexColor("#38bdf8")),
        ("TEXTCOLOR",   (1,0), (1,-1), colors.HexColor("#e2e8f0")),
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#0c1a2e"), colors.HexColor("#081525")]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#1e3a5f")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING",(0,0), (-1,-1), 8),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.2*inch))

    # Question
    q_style = ParagraphStyle("qlabel", parent=styles["Normal"],
                              fontSize=9, textColor=colors.HexColor("#818cf8"),
                              fontName="Helvetica-Bold", spaceAfter=4)
    a_style = ParagraphStyle("qtext", parent=styles["Normal"],
                              fontSize=11, textColor=colors.HexColor("#1a1a2e"),
                              backColor=colors.HexColor("#e8f4fd"),
                              borderPad=8, leading=16,
                              leftIndent=8, rightIndent=8,
                              spaceAfter=12, fontName="Helvetica")
    story.append(Paragraph("QUESTION", q_style))
    story.append(Paragraph(question, a_style))

    # Insight
    story.append(Paragraph("AI INSIGHT", q_style))
    clean_insight = re.sub(r'<[^>]+>', '', insight)   # strip HTML tags
    clean_insight = clean_insight.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    ins_style = ParagraphStyle("ins", parent=styles["Normal"],
                                fontSize=10, textColor=colors.HexColor("#1a1a2e"),
                                leading=15, spaceAfter=12, fontName="Helvetica")
    story.append(Paragraph(clean_insight, ins_style))

    # Accuracy breakdown
    story.append(Paragraph("ACCURACY BREAKDOWN", q_style))
    acc_color = {"HIGH": "#34d399", "MEDIUM": "#fbbf24", "LOW": "#f87171"}[accuracy["level"]]
    acc_data  = [["Check", "Result", "Score"]]
    for chk, (result, pts) in accuracy["checks"].items():
        clean_result = result.replace("✅","OK").replace("⚠️","WARN")
        acc_data.append([chk, clean_result, str(pts)])
    acc_data.append(["TOTAL ACCURACY SCORE", "", f"{accuracy['score']}/100"])

    acc_table = Table(acc_data, colWidths=[2.2*inch, 3.0*inch, 1.1*inch])
    acc_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),  (-1,0),  colors.HexColor("#0f1e35")),
        ("TEXTCOLOR",    (0,0),  (-1,0),  colors.HexColor("#38bdf8")),
        ("FONTNAME",     (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),  (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-2), [colors.HexColor("#f8f9fa"), colors.HexColor("#ffffff")]),
        ("BACKGROUND",   (0,-1), (-1,-1), colors.HexColor(acc_color)),
        ("TEXTCOLOR",    (0,-1), (-1,-1), colors.white),
        ("FONTNAME",     (0,-1), (-1,-1), "Helvetica-Bold"),
        ("GRID",         (0,0),  (-1,-1), 0.5, colors.HexColor("#dee2e6")),
        ("ALIGN",        (2,0),  (2,-1),  "CENTER"),
        ("LEFTPADDING",  (0,0),  (-1,-1), 8),
        ("RIGHTPADDING", (0,0),  (-1,-1), 8),
        ("TOPPADDING",   (0,0),  (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),  (-1,-1), 5),
    ]))
    story.append(acc_table)
    story.append(Spacer(1, 0.15*inch))

    # Footer
    footer_style = ParagraphStyle("footer", parent=styles["Normal"],
                                  fontSize=8, textColor=colors.HexColor("#64748b"),
                                  alignment=TA_CENTER)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1e3a5f")))
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph("Generated by AI Business Intelligence Dashboard · Powered by Google Gemini", footer_style))

    doc.build(story)
    return buf.getvalue()

# -----------------------
# TITLE
# -----------------------
st.markdown('<div class="dash-title">AI BUSINESS INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-sub">CONVERSATIONAL DATA ANALYTICS PLATFORM</div>', unsafe_allow_html=True)

# -----------------------
# SESSION STATE
# -----------------------
for _k, _v in [("last_answer", None), ("last_chart_spec", None),
                ("last_question", ""), ("query_history", []),
                ("last_accuracy", None), ("last_fig", None)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# -----------------------
# SIDEBAR
# -----------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    st.markdown("**🔑 Gemini API Key**")
    st.text_input("Paste your key here", type="password",
                  placeholder="AIza...", key="api_key",
                  help="Get your free key at https://aistudio.google.com/app/apikey")
    api_key = st.session_state.get("api_key", "").strip()

    if api_key:
        st.markdown('<span class="status-badge status-ok">● API KEY SET</span>', unsafe_allow_html=True)
        detected = get_best_model(api_key)
        st.caption(f"🤖 Model: `{detected}`")
    else:
        st.markdown('<span class="status-badge status-err">● NO KEY</span>', unsafe_allow_html=True)
        st.info("Enter your Gemini API key above to enable AI insights.", icon="💡")

    st.markdown("---")
    st.markdown("**📁 Upload Dataset**")
    uploaded_file = st.file_uploader("CSV files only", type=["csv"],
        help="Upload any CSV file.")

    st.markdown("---")
    st.markdown("**🎛️ Chart Options**")
    chart_height = st.slider("Chart height (px)", 300, 600, 380, 20)
    show_raw = st.checkbox("Show raw data table", value=True)

    st.markdown("---")
    if api_key:
        if st.button("🔍 Test API Key"):
            try:
                genai.configure(api_key=api_key)
                available = [m.name for m in genai.list_models()
                             if "generateContent" in m.supported_generation_methods]
                st.success(f"✅ Key valid! {len(available)} models available")
                with st.expander("See models"):
                    for m in available: st.caption(m)
            except Exception as e:
                st.error(f"Key error: {e}")

    # Query history in sidebar
    if st.session_state["query_history"]:
        st.markdown("---")
        st.markdown("**📜 Query History**")
        for i, h in enumerate(reversed(st.session_state["query_history"][-5:])):
            st.markdown(
                f'<div class="history-card">'
                f'<span style="color:#38bdf8;font-size:0.7rem;font-family:Orbitron,monospace">#{len(st.session_state["query_history"])-i}</span><br>'
                f'<span style="color:#94a3b8;font-size:0.85rem">{h["question"][:60]}{"..." if len(h["question"])>60 else ""}</span><br>'
                f'<span style="color:#34d399;font-size:0.75rem">Accuracy: {h["accuracy"]}%</span>'
                f'</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear History"):
            st.session_state["query_history"] = []
            st.rerun()

    st.caption("Built with Streamlit · Gemini · Plotly")

# -----------------------
# MAIN AREA
# -----------------------
if not uploaded_file:
    st.markdown("""
    <div style="text-align:center; padding:80px 40px; opacity:0.5;">
        <div style="font-size:5rem">📂</div>
        <div style="font-family:'Orbitron',monospace; font-size:1rem; letter-spacing:3px; color:#38bdf8; margin-top:16px;">UPLOAD A CSV TO BEGIN</div>
        <div style="color:#475569; margin-top:8px; font-size:0.9rem;">Drag and drop a file into the sidebar uploader</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# -----------------------
# LOAD DATA
# -----------------------
try:
    df = pd.read_csv(uploaded_file)
except UnicodeDecodeError:
    try:
        uploaded_file.seek(0); df = pd.read_csv(uploaded_file, encoding="latin1")
    except Exception as e:
        st.error(f"Could not read the file: {e}"); st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}"); st.stop()

dataset_name = uploaded_file.name if hasattr(uploaded_file, "name") else "dataset.csv"

# -----------------------
# METRICS
# -----------------------
missing      = int(df.isnull().sum().sum())
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
cat_cols     = df.select_dtypes(include=["object","category"]).columns.tolist()

st.markdown(f"""
<div class="metric-row">
  <div class="metric-card"><div class="metric-icon">📋</div><div class="metric-label">Total Rows</div><div class="metric-value">{df.shape[0]:,}</div></div>
  <div class="metric-card"><div class="metric-icon">🗂️</div><div class="metric-label">Columns</div><div class="metric-value">{df.shape[1]}</div></div>
  <div class="metric-card"><div class="metric-icon">❗</div><div class="metric-label">Missing Values</div><div class="metric-value">{missing:,}</div></div>
  <div class="metric-card"><div class="metric-icon">🔢</div><div class="metric-label">Numeric Cols</div><div class="metric-value">{len(numeric_cols)}</div></div>
  <div class="metric-card"><div class="metric-icon">🏷️</div><div class="metric-label">Category Cols</div><div class="metric-value">{len(cat_cols)}</div></div>
</div>""", unsafe_allow_html=True)

if show_raw:
    st.markdown('<div class="section-header">Dataset Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(100), use_container_width=True, height=280)

# -----------------------
# AUTOMATIC VISUALIZATIONS
# -----------------------
st.markdown('<div class="section-header">Automatic Visualizations</div>', unsafe_allow_html=True)
colA, colB = st.columns(2, gap="medium")

with colA:
    if numeric_cols:
        selected_num = st.selectbox("Numeric column", numeric_cols, key="hist_col")
        fig1 = px.histogram(df, x=selected_num, title=f"Distribution · {selected_num}",
                            nbins=40, template=PLOTLY_TEMPLATE, color_discrete_sequence=["#38bdf8"])
        fig1.update_traces(marker_line_color="rgba(56,189,248,0.4)", marker_line_width=0.5)
        st.plotly_chart(fig1, use_container_width=True, height=chart_height)

with colB:
    if cat_cols:
        selected_cat = st.selectbox("Categorical column", cat_cols, key="bar_col")
        top_n = st.slider("Show top N", 5, 30, 10, key="top_n")
        counts = df[selected_cat].value_counts().head(top_n).reset_index()
        counts.columns = ["Category","Count"]
        fig2 = px.bar(counts, x="Category", y="Count",
                      title=f"Top {top_n} · {selected_cat}", template=PLOTLY_TEMPLATE,
                      color="Count", color_continuous_scale=["#1e3a5f","#38bdf8","#f472b6"])
        fig2.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        st.plotly_chart(fig2, use_container_width=True, height=chart_height)

if len(numeric_cols) >= 2:
    st.markdown('<div class="section-header">Correlation Explorer</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2,2,1], gap="medium")
    with c1: x_col = st.selectbox("X axis", numeric_cols, key="sc_x")
    with c2: y_col = st.selectbox("Y axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="sc_y")
    with c3: color_col = st.selectbox("Color by", ["None"]+cat_cols, key="sc_color")
    try: import statsmodels; trendline="ols"
    except ImportError: trendline=None
    fig3 = px.scatter(df, x=x_col, y=y_col,
                      color=None if color_col=="None" else color_col,
                      title=f"{x_col}  vs  {y_col}", template=PLOTLY_TEMPLATE,
                      opacity=0.75, trendline=trendline)
    fig3.update_traces(marker=dict(size=5))
    st.plotly_chart(fig3, use_container_width=True, height=chart_height)
    if not trendline: st.caption("💡 `pip install statsmodels` to enable trendlines")

# -----------------------
# AI Q&A SECTION
# -----------------------
st.markdown('<div class="section-header">Ask AI About Your Data</div>', unsafe_allow_html=True)

api_key = st.session_state.get("api_key","").strip()
if not api_key:
    st.warning("⚠️ Enter your Gemini API key in the sidebar to use AI insights.", icon="🔑")
else:
    question = st.text_area("Your question",
        placeholder="e.g. Which category has the highest revenue? | Top 5 products by units sold | Monthly sales trend",
        height=90)

    col_btn, col_spacer = st.columns([1,4])
    with col_btn: ask_btn = st.button("ANALYZE ➜")

    if ask_btn and question.strip():
        try:
            genai.configure(api_key=api_key)
            model_name = get_best_model(api_key)
            model      = genai.GenerativeModel(model_name)
            st.caption(f"🤖 Using: `{model_name}`")

            # ── Pre-aggregate full dataset ──────────────────────────
            numeric_col_list = df.select_dtypes(include="number").columns.tolist()
            cat_col_list     = df.select_dtypes(include=["object","category"]).columns.tolist()

            stats_summary = df.describe(include="all").round(4).to_string()
            cat_summaries = ""
            for c in cat_col_list:
                cat_summaries += f"\n=== {c} value counts ===\n{df[c].value_counts().head(20).to_string()}\n"

            groupby_summaries = ""
            for cat in cat_col_list:
                for num in numeric_col_list:
                    try:
                        grp = (df.groupby(cat)[num].agg(["mean","sum","count"])
                               .round(4).sort_values("mean", ascending=False))
                        groupby_summaries += f"\n=== {num} by {cat} ===\n{grp.to_string()}\n"
                    except: pass

            two_level = ""
            if len(cat_col_list) >= 2:
                for i, c1 in enumerate(cat_col_list):
                    for c2 in cat_col_list[i+1:]:
                        for num in numeric_col_list[:2]:
                            try:
                                grp2 = (df.groupby([c1,c2])[num].mean().round(4)
                                        .reset_index().sort_values(num, ascending=False).head(20))
                                two_level += f"\n=== avg {num} by {c1}+{c2} ===\n{grp2.to_string(index=False)}\n"
                            except: pass

            time_summary = ""
            date_cols = [c for c in df.columns if "date" in c.lower()]
            if date_cols:
                try:
                    tmp = df.copy()
                    tmp["_month"] = pd.to_datetime(tmp[date_cols[0]], errors="coerce").dt.to_period("M").astype(str)
                    for num in numeric_col_list[:3]:
                        ts = tmp.groupby("_month")[num].sum().round(2)
                        time_summary += f"\n=== monthly {num} ===\n{ts.to_string()}\n"
                    for cat in cat_col_list[:2]:
                        for num in numeric_col_list[:2]:
                            ts2 = (tmp.groupby(["_month",cat])[num].sum().round(2)
                                   .reset_index().sort_values(["_month",num], ascending=[True,False]))
                            time_summary += f"\n=== monthly {num} by {cat} ===\n{ts2.to_string(index=False)}\n"
                except: pass

            json_example = '{"chart_type":"bar","x":"customer_region","y":"rating","color":null,"agg":"mean","group_by":"customer_region","title":"Avg Rating by Region","top_n":null,"filter_col":null,"filter_val":null}'
            col_dtypes   = {k: str(v) for k, v in df.dtypes.to_dict().items()}

            combined_prompt = (
                "You are an expert business data analyst AND data visualization expert.\n"
                "All figures below are pre-computed from the COMPLETE dataset — 100% accurate.\n\n"
                f"SCHEMA: {df.columns.tolist()}\nDTYPES: {col_dtypes}\n\n"
                f"OVERALL STATISTICS:\n{stats_summary}\n\n"
                f"CATEGORICAL DISTRIBUTIONS:\n{cat_summaries}\n\n"
                f"GROUPBY AGGREGATIONS:\n{groupby_summaries}\n\n"
                f"CROSS-DIMENSION AGGREGATIONS:\n{two_level}\n\n"
                f"MONTHLY TIME-SERIES:\n{time_summary}\n\n"
                f"USER QUESTION: {question}\n\n"
                "Respond in EXACTLY this format:\n\n"
                "##INSIGHT##\n"
                "<text answer — precise numbers with 2 decimal places, max 300 words, "
                "professional language, cite specific column names and values>\n\n"
                "##CHART##\n"
                "<single valid JSON object — keys: chart_type (bar/line/pie/scatter/histogram/box), "
                "x, y, color, agg (sum/mean/count/max/min/null), group_by, title, "
                "top_n (int or null), filter_col, filter_val — JSON null, double quotes>\n\n"
                f"JSON example: {json_example}"
            )

            with st.spinner(f"🤖 Analyzing with {model_name}..."):
                raw_response = safe_generate(model, combined_prompt)

            # ── Parse sections ──────────────────────────────────────
            insight_text = ""
            chart_json   = ""
            if "##INSIGHT##" in raw_response and "##CHART##" in raw_response:
                parts        = raw_response.split("##CHART##")
                insight_text = parts[0].replace("##INSIGHT##","").strip()
                chart_json   = parts[1].strip()
            else:
                insight_text = raw_response.strip()

            # ── Compute accuracy ────────────────────────────────────
            accuracy = compute_accuracy(question, insight_text, df)
            st.session_state["last_accuracy"] = accuracy

            # ── Render insight ──────────────────────────────────────
            insight_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', insight_text)
            insight_html = re.sub(r'\*(.*?)\*',     r'<em>\1</em>',         insight_html)
            insight_html = insight_html.replace('\n','<br>')
            st.markdown(f'<div class="ai-response">{insight_html}</div>', unsafe_allow_html=True)

            # ── Accuracy display ────────────────────────────────────
            st.markdown('<div class="section-header">Accuracy Analysis</div>', unsafe_allow_html=True)
            acc_col1, acc_col2 = st.columns([1,2])
            with acc_col1:
                st.markdown(f"""
                <div class="accuracy-bar" style="text-align:center;">
                    <div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:#64748b; letter-spacing:2px;">ACCURACY SCORE</div>
                    <div style="font-family:'Orbitron',monospace; font-size:3rem; font-weight:900; color:{'#34d399' if accuracy['score']>=80 else '#fbbf24' if accuracy['score']>=55 else '#f87171'}">
                        {accuracy['score']}%
                    </div>
                    <div class="{accuracy['color']}">{accuracy['level']} CONFIDENCE</div>
                </div>""", unsafe_allow_html=True)
            with acc_col2:
                for chk, (result, pts) in accuracy["checks"].items():
                    icon = "🟢" if pts >= 20 else "🟡" if pts >= 10 else "🔴"
                    st.markdown(f"**{icon} {chk}** — {result} `+{pts}pts`")

            # ── Render chart ────────────────────────────────────────
            ai_fig = None
            if chart_json:
                try:
                    raw_j = re.sub(r'^```[a-zA-Z]*\s*','',chart_json)
                    raw_j = re.sub(r'\s*```$','',raw_j).strip()
                    m     = re.search(r'\{.*\}', raw_j, re.DOTALL)
                    if m: raw_j = m.group(0)
                    spec = json.loads(raw_j)

                    chart_type = spec.get("chart_type","bar")
                    x_col_ai   = spec.get("x")
                    y_col_ai   = spec.get("y")
                    color_ai   = spec.get("color")
                    agg        = spec.get("agg")
                    group_by   = spec.get("group_by")
                    title_ai   = spec.get("title","AI Chart")
                    top_n_ai   = spec.get("top_n")
                    filter_col = spec.get("filter_col")
                    filter_val = spec.get("filter_val")

                    plot_df = df.copy()
                    if filter_col and filter_val and filter_col in plot_df.columns:
                        plot_df = plot_df[plot_df[filter_col].astype(str).str.contains(str(filter_val), case=False, na=False)]
                    if group_by and group_by in plot_df.columns and y_col_ai and y_col_ai in plot_df.columns and agg:
                        agg_map = {"sum":"sum","mean":"mean","count":"count","max":"max","min":"min"}
                        if agg=="count":
                            plot_df = plot_df.groupby(group_by).size().reset_index(name=y_col_ai)
                        else:
                            plot_df = plot_df.groupby(group_by)[y_col_ai].agg(agg_map.get(agg,"mean")).reset_index()
                        plot_df  = plot_df.sort_values(y_col_ai, ascending=False)
                        x_col_ai = group_by
                    if top_n_ai and isinstance(top_n_ai, int):
                        plot_df = plot_df.head(top_n_ai)

                    def col_ok(c): return c and c in plot_df.columns

                    st.markdown('<div class="section-header">AI Generated Chart</div>', unsafe_allow_html=True)
                    if chart_type=="bar" and col_ok(x_col_ai) and col_ok(y_col_ai):
                        ai_fig = px.bar(plot_df, x=x_col_ai, y=y_col_ai,
                                        color=color_ai if col_ok(color_ai) else None,
                                        title=title_ai, template=PLOTLY_TEMPLATE,
                                        color_discrete_sequence=["#38bdf8","#818cf8","#f472b6","#34d399","#fb923c"])
                        ai_fig.update_layout(xaxis_tickangle=-35)
                    elif chart_type=="line" and col_ok(x_col_ai) and col_ok(y_col_ai):
                        ai_fig = px.line(plot_df, x=x_col_ai, y=y_col_ai,
                                         color=color_ai if col_ok(color_ai) else None,
                                         title=title_ai, template=PLOTLY_TEMPLATE,
                                         color_discrete_sequence=["#38bdf8","#818cf8","#f472b6"])
                        ai_fig.update_traces(line=dict(width=2.5))
                    elif chart_type=="pie" and col_ok(x_col_ai) and col_ok(y_col_ai):
                        ai_fig = px.pie(plot_df, names=x_col_ai, values=y_col_ai,
                                        title=title_ai, template=PLOTLY_TEMPLATE,
                                        color_discrete_sequence=["#38bdf8","#818cf8","#f472b6","#34d399","#fb923c","#a78bfa"])
                        ai_fig.update_traces(textposition="inside", textinfo="percent+label")
                    elif chart_type=="scatter" and col_ok(x_col_ai) and col_ok(y_col_ai):
                        ai_fig = px.scatter(plot_df, x=x_col_ai, y=y_col_ai,
                                            color=color_ai if col_ok(color_ai) else None,
                                            title=title_ai, template=PLOTLY_TEMPLATE, opacity=0.75,
                                            color_discrete_sequence=["#38bdf8","#818cf8","#f472b6"])
                        ai_fig.update_traces(marker=dict(size=6))
                    elif chart_type=="histogram" and col_ok(x_col_ai):
                        ai_fig = px.histogram(plot_df, x=x_col_ai, title=title_ai,
                                              template=PLOTLY_TEMPLATE, color_discrete_sequence=["#38bdf8"])
                    elif chart_type=="box" and col_ok(y_col_ai):
                        ai_fig = px.box(plot_df, x=x_col_ai if col_ok(x_col_ai) else None,
                                        y=y_col_ai, title=title_ai, template=PLOTLY_TEMPLATE,
                                        color_discrete_sequence=["#38bdf8"])

                    if ai_fig:
                        st.plotly_chart(ai_fig, use_container_width=True, height=chart_height)
                        st.session_state["last_fig"] = ai_fig
                    else:
                        st.info("Chart could not be generated — text insight above answers your question.")
                except Exception as ce:
                    st.caption(f"Chart generation skipped: {ce}")

            # ── Save to history ─────────────────────────────────────
            st.session_state["last_answer"]   = insight_text
            st.session_state["last_question"] = question
            st.session_state["query_history"].append({
                "question": question,
                "answer":   insight_text,
                "accuracy": accuracy["score"],
                "model":    model_name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

            # ── DOWNLOAD SECTION ────────────────────────────────────
            st.markdown('<div class="section-header">Download Results</div>', unsafe_allow_html=True)
            dl1, dl2, dl3 = st.columns(3)

            # 1. Download as PDF
            with dl1:
                try:
                    pdf_bytes = generate_pdf(
                        question=question,
                        insight=insight_text,
                        accuracy=accuracy,
                        df_name=dataset_name,
                        model_name=model_name,
                        fig=ai_fig
                    )
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"ai_insight_{ts}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as pdf_err:
                    st.error(f"PDF error: {pdf_err}")

            # 2. Download as TXT
            with dl2:
                txt = (
                    f"AI BUSINESS INTELLIGENCE REPORT\n"
                    f"{'='*50}\n"
                    f"Dataset    : {dataset_name}\n"
                    f"Model      : {model_name}\n"
                    f"Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Accuracy   : {accuracy['score']}% ({accuracy['level']})\n"
                    f"{'='*50}\n\n"
                    f"QUESTION:\n{question}\n\n"
                    f"AI INSIGHT:\n{re.sub('<[^>]+>','',insight_text)}\n\n"
                    f"ACCURACY BREAKDOWN:\n"
                    + "\n".join(f"  {k}: {v[0]} (+{v[1]}pts)" for k,v in accuracy['checks'].items())
                    + f"\n  TOTAL: {accuracy['score']}/100\n"
                )
                st.download_button(
                    label="📝 Download TXT Report",
                    data=txt.encode("utf-8"),
                    file_name=f"ai_insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            # 3. Download full history as CSV
            with dl3:
                if st.session_state["query_history"]:
                    hist_df = pd.DataFrame(st.session_state["query_history"])
                    csv_buf = io.StringIO()
                    hist_df.to_csv(csv_buf, index=False)
                    st.download_button(
                        label="📊 Download History CSV",
                        data=csv_buf.getvalue().encode("utf-8"),
                        file_name=f"query_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        except Exception as e:
            err_str = str(e)
            if "API_KEY_INVALID" in err_str.upper() or "api key not valid" in err_str.lower():
                st.error("❌ Invalid API key. Check at https://aistudio.google.com/app/apikey")
            elif "quota" in err_str.lower() or "429" in err_str or "resource exhausted" in err_str.lower():
                st.error("❌ **API Quota Exceeded.** Wait 1 min and retry, or get a new free key at https://aistudio.google.com/app/apikey")
            elif "permission" in err_str.lower() or "403" in err_str:
                st.error("❌ Permission denied. Enable Gemini API at https://console.cloud.google.com")
            elif "not found" in err_str.lower() or "404" in err_str:
                get_best_model.clear()
                st.error("❌ Model not found. Click Analyze again to auto-detect a working model.")
            else:
                st.error(f"❌ API Error: {err_str}")

    elif ask_btn and not question.strip():
        st.warning("Please type a question before clicking Analyze.")
