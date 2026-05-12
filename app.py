import streamlit as st
import pandas as pd
import io
import math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ──────────────────────────────────────────────────────────────────────────────
# PAY STRUCTURE
# ──────────────────────────────────────────────────────────────────────────────
PAY_STRUCTURE = {
    "A5": {"score": 0.5, "salary": 2625.09, "mobility": 780},
    "A6": {"score": 0.6, "salary": 2756.35, "mobility": 780},
    "A7": {"score": 0.7, "salary": 2894.16, "mobility": 780},
    "A8": {"score": 0.8, "salary": 3038.87, "mobility": 780},
    "A9": {"score": 0.9, "salary": 3190.81, "mobility": 780},
    "B0": {"score": 1.0, "salary": 3350.35, "mobility": 930},
    "B1": {"score": 1.1, "salary": 3517.87, "mobility": 930},
    "B2": {"score": 1.2, "salary": 3693.77, "mobility": 930},
    "B3": {"score": 1.3, "salary": 3878.45, "mobility": 930},
    "B4": {"score": 1.4, "salary": 4072.38, "mobility": 930},
    "B5": {"score": 1.5, "salary": 4276.00, "mobility": 930},
    "B6": {"score": 1.6, "salary": 4489.80, "mobility": 930},
    "B7": {"score": 1.7, "salary": 4714.29, "mobility": 930},
    "B8": {"score": 1.8, "salary": 4950.00, "mobility": 930},
    "B9": {"score": 1.9, "salary": 5197.50, "mobility": 930},
    "C0": {"score": 2.0, "salary": 5457.38, "mobility": 1080},
    "C1": {"score": 2.1, "salary": 5730.24, "mobility": 1080},
    "C2": {"score": 2.2, "salary": 6016.76, "mobility": 1080},
    "C3": {"score": 2.3, "salary": 6317.59, "mobility": 1080},
    "C4": {"score": 2.4, "salary": 6633.47, "mobility": 1080},
    "C5": {"score": 2.5, "salary": 6965.15, "mobility": 1080},
    "C6": {"score": 2.6, "salary": 7243.75, "mobility": 1080},
    "C7": {"score": 2.7, "salary": 7533.50, "mobility": 1080},
    "C8": {"score": 2.8, "salary": 7834.84, "mobility": 1080},
    "C9": {"score": 2.9, "salary": 8148.24, "mobility": 1080},
    "D0": {"score": 3.0, "salary": 8474.17, "mobility": 1230},
    "D1": {"score": 3.1, "salary": 8813.13, "mobility": 1230},
    "D2": {"score": 3.2, "salary": 9165.66, "mobility": 1230},
    "D3": {"score": 3.3, "salary": 9532.28, "mobility": 1230},
    "D4": {"score": 3.4, "salary": 9913.58, "mobility": 1230},
    "D5": {"score": 3.5, "salary": 10310.12, "mobility": 1230},
    "D6": {"score": 3.6, "salary": 10722.52, "mobility": 1230},
    "D7": {"score": 3.7, "salary": 11151.42, "mobility": 1230},
    "D8": {"score": 3.8, "salary": 11597.48, "mobility": 1230},
    "D9": {"score": 3.9, "salary": 12061.38, "mobility": 1230},
    "E0": {"score": 4.0, "salary": 12543.84, "mobility": 1380},
    "E1": {"score": 4.1, "salary": 13045.59, "mobility": 1380},
    "E2": {"score": 4.2, "salary": 13567.41, "mobility": 1380},
    "E3": {"score": 4.3, "salary": 14110.11, "mobility": 1380},
    "E4": {"score": 4.4, "salary": 14674.51, "mobility": 1380},
    "E5": {"score": 4.5, "salary": 15261.49, "mobility": 1380},
}

SCORE_LABELS = {
    0: "0 — Not present",
    1: "1 — Basic",
    2: "2 — Developing",
    3: "3 — Proficient",
    4: "4 — Advanced",
    5: "5 — Expert",
}

PAGES = [
    ("Job Information",       "job_info"),
    ("Technical Competency",  "technical"),
    ("Behavioural Competency","behavioural"),
    ("Effort",                "effort"),
    ("Professional Capital",  "professional"),
    ("Working Conditions",    "working"),
    ("Responsibility",        "responsibility"),
    ("Results & Pay Proposal","results"),
    ("Reward Strategy",       "info"),
]

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE — initialise all keys once so widgets never reset on navigate
# ──────────────────────────────────────────────────────────────────────────────
DEFAULTS = {
    # Job info
    "job_name": "", "evaluator": "",
    # Technical competency
    "tc_legal": 2, "tc_data": 2, "tc_strategy": 2, "tc_leadership": 2, "tc_transformational": 2,
    # Behavioural competency
    "bc_ic_cp": 2, "bc_ic_cs": 2, "bc_ic_team": 2, "bc_ic_org": 2,
    "bc_freq": 2, "bc_cons": 2, "bc_conf": 2,
    # Effort
    "ef_conc": 2, "ef_prob": 2, "ef_info": 2, "ef_multi": 2, "ef_switch": 2,
    "ef_own": 2, "ef_oth": 2, "ef_conf": 2, "ef_press": 2,
    # Professional capital
    "pc_cred": 2, "pc_rel": 2, "pc_org": 2,
    # Working conditions
    "wc_sched": 2, "wc_travel": 2, "wc_social": 2,
    # Responsibility
    "resp_scope": 2, "resp_auto": 2, "resp_rev": 2, "resp_dec": 2,
    # Comments
    "comment_tc": "", "comment_bc": "", "comment_ef": "",
    "comment_pc": "", "comment_wc": "", "comment_resp": "", "overall_comments": "",
    # Navigation
    "_page": "job_info",
}

def init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ──────────────────────────────────────────────────────────────────────────────
STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Hide sidebar collapse toggle ── */
[data-testid="collapsedControl"] { display: none !important; }

/* ── Sidebar — light theme ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #D8EBE7 !important;
}
[data-testid="stSidebar"] * { color: #164A41 !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }

.sidebar-logo {
    background: #164A41;
    padding: 22px 20px 18px 20px;
    border-bottom: 1px solid #D8EBE7;
    margin-bottom: 6px;
}
.sidebar-logo img { height: 34px; filter: brightness(0) invert(1); }
.sidebar-brand {
    color: rgba(255,255,255,0.65) !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 10px;
}

/* Nav buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 7px !important;
    color: #4A7A70 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 9px 14px !important;
    width: 100% !important;
    transition: background 0.15s, color 0.15s !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #EFF7F4 !important;
    color: #164A41 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #E8F4F1 !important;
    border-left: 3px solid #164A41 !important;
    color: #164A41 !important;
    font-weight: 600 !important;
}

.score-preview {
    margin: 14px 10px 6px 10px;
    background: #F5FAF8;
    border-radius: 10px;
    padding: 14px 16px;
    border: 1px solid #D8EBE7;
}
.score-preview-label {
    font-size: 10px !important;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7FA89F !important;
    margin-bottom: 8px;
}
.score-big { font-size: 30px !important; font-weight: 700 !important; color: #164A41 !important; line-height: 1.1; }
.score-level { font-size: 14px !important; font-weight: 600 !important; color: #E07B39 !important; margin-top: 2px; }
.score-salary { font-size: 11px !important; color: #7FA89F !important; margin-top: 3px; }
.score-bar-bg { background: #D8EBE7; border-radius: 4px; height: 4px; margin-top: 10px; overflow: hidden; }
.score-bar-fill { height: 4px; border-radius: 4px; background: linear-gradient(90deg,#164A41,#E07B39); }

/* ── Main content ── */
.main .block-container { padding: 2rem 2.5rem 3rem 2.5rem; max-width: 960px; }

/* ── Page header ── */
.page-header { margin-bottom: 26px; padding-bottom: 18px; border-bottom: 2px solid #D8EBE7; }
.page-header-badge {
    display: inline-flex; align-items: center;
    background: #E8F4F1; color: #164A41;
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 3px 10px; border-radius: 20px; margin-bottom: 10px;
}
.page-title {
    font-size: 24px !important; font-weight: 700 !important;
    color: #164A41 !important; margin: 0 0 5px 0 !important; letter-spacing: -0.4px;
}
.page-subtitle { font-size: 13.5px; color: #64748B; margin: 0; }

/* ── Cards ── */
.card {
    background: #FFFFFF; border: 1px solid #D8EBE7; border-radius: 12px;
    padding: 20px 24px; margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(22,74,65,0.06);
}
.card-title {
    font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #94A3B8; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #EDF2F7;
}

/* ── Info panel ── */
.info-panel {
    background: #EFF7F4; border: 1px solid #B8D8D2; border-left: 4px solid #164A41;
    border-radius: 0 8px 8px 0; padding: 13px 17px; margin-bottom: 20px;
    font-size: 13.5px; color: #164A41; line-height: 1.6;
}

/* ── Metric cards ── */
.metric-card {
    background: #FFFFFF; border: 1px solid #D8EBE7; border-radius: 10px;
    padding: 16px 18px; text-align: center;
    box-shadow: 0 1px 3px rgba(22,74,65,0.06); height: 100%;
}
.metric-label { font-size: 11px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: #94A3B8; margin-bottom: 6px; }
.metric-value { font-size: 26px; font-weight: 700; color: #164A41; line-height: 1.1; }
.metric-highlight { border: 2px solid #E07B39 !important; }
.metric-highlight .metric-value { color: #E07B39; }

/* ── Pay level badge ── */
.pay-level-badge {
    display: inline-block;
    background: linear-gradient(135deg,#164A41 0%,#1D5C4E 100%);
    color: #FFFFFF; font-size: 22px; font-weight: 700;
    padding: 6px 18px; border-radius: 8px; letter-spacing: 2px;
}

/* ── Dimension score row ── */
.dim-row { display: flex; align-items: center; padding: 9px 0; border-bottom: 1px solid #F1F5F9; }
.dim-row:last-child { border-bottom: none; }
.dim-name { flex: 1; font-size: 13px; color: #334155; font-weight: 500; }
.dim-weight { font-size: 11px; color: #94A3B8; width: 48px; text-align: right; margin-right: 12px; }
.dim-score-bar { flex: 0 0 110px; }
.dim-score-bar-bg { background: #EDF2F7; border-radius: 4px; height: 6px; }
.dim-score-bar-fill { height: 6px; border-radius: 4px; background: linear-gradient(90deg,#164A41,#E07B39); }
.dim-score-val { font-size: 12px; font-weight: 600; color: #164A41; width: 34px; text-align: right; margin-left: 10px; }

/* ── Compensation table ── */
.comp-table { width: 100%; border-collapse: collapse; }
.comp-table tr { border-bottom: 1px solid #EDF2F7; }
.comp-table tr:last-child { border-bottom: none; }
.comp-table td { padding: 8px 10px; font-size: 13px; }
.comp-table td:first-child { color: #64748B; font-weight: 500; }
.comp-table td:last-child { color: #164A41; font-weight: 600; text-align: right; }
.comp-table .comp-hi td { background: #EFF7F4; }
.comp-table .comp-hi td:last-child { color: #E07B39; }

/* ── Hint text under sliders ── */
.sub-dim-hint { font-size: 11.5px; color: #94A3B8; margin-bottom: 4px; font-style: italic; }

/* ── Comment area ── */
.comment-header {
    font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #94A3B8; margin-bottom: 6px;
}

/* ── Computed score chip ── */
.computed-chip {
    background: #EFF7F4; border-radius: 8px; padding: 10px 14px;
    border: 1px solid #B8D8D2; font-size: 13.5px; margin: 6px 0 8px 0;
}

/* ── Anchor radio blocks ── */
div[data-testid="stRadio"] > label { font-size: 14px !important; font-weight: 600 !important; color: #164A41 !important; margin-bottom: 10px !important; }
div[data-testid="stRadio"] > div { gap: 6px !important; }
div[data-testid="stRadio"] > div > label {
    background: #F5FAF8 !important;
    border: 1px solid #D8EBE7 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
    transition: background 0.15s, border-color 0.15s !important;
}
div[data-testid="stRadio"] > div > label:hover {
    background: #EBF5F1 !important;
    border-color: #164A41 !important;
}
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: #E8F4F1 !important;
    border-color: #164A41 !important;
    border-left: 3px solid #164A41 !important;
}
div[data-testid="stRadio"] > div > label p { font-size: 13px !important; color: #334155 !important; line-height: 1.55 !important; margin: 0 !important; }

/* ── Streamlit widget overrides ── */
div[data-testid="stSelectSlider"] label { font-size: 13.5px !important; font-weight: 500 !important; color: #334155 !important; }
.stTextArea textarea { font-size: 13.5px !important; border-color: #D8EBE7 !important; border-radius: 8px !important; }
.stTextInput input { font-size: 13.5px !important; border-color: #D8EBE7 !important; border-radius: 8px !important; }
.stDateInput input { font-size: 13.5px !important; border-radius: 8px !important; }

/* Primary button (main area) */
.main .stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#164A41 0%,#1D5C4E 100%) !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 14px !important; color: #FFFFFF !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg,#E07B39 0%,#F5A462 100%) !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; color: #FFFFFF !important;
}
button[data-baseweb="tab"] { font-size: 13px !important; font-weight: 500 !important; }
details summary p { font-size: 13.5px !important; font-weight: 600 !important; color: #164A41 !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; }
</style>
"""

# ──────────────────────────────────────────────────────────────────────────────
# SCORING LOGIC
# ──────────────────────────────────────────────────────────────────────────────
def calc_ic(subs):
    if subs.count(5) >= 2: return 5
    if subs.count(4) >= 2: return 4
    return round(sum(subs) / len(subs))

def calculate_scores():
    s = st.session_state
    tc = sum(s[k] for k in ["tc_legal","tc_data","tc_strategy","tc_leadership","tc_transformational"]) / 5
    ic_subs = [s[k] for k in ["bc_ic_cp","bc_ic_cs","bc_ic_team","bc_ic_org"]]
    ic = calc_ic(ic_subs)
    ic_n, fr_n = ic/5, s["bc_freq"]/5
    co_n, cf_n = s["bc_cons"]/5, s["bc_conf"]/5
    bc = round((ic_n**0.3 * fr_n**0.25 * co_n**0.25 * cf_n**0.2)*5, 2) if all(v>0 for v in [ic_n,fr_n,co_n,cf_n]) else 0.0
    mental = (sum(s[k] for k in ["ef_conc","ef_prob","ef_info","ef_multi","ef_switch"]) / 5) * 0.5
    emot   = (sum(s[k] for k in ["ef_own","ef_oth","ef_conf","ef_press"]) / 4) * 0.5
    effort = mental + emot
    pc   = sum(s[k] for k in ["pc_cred","pc_rel","pc_org"]) / 3
    wc   = sum(s[k] for k in ["wc_sched","wc_travel","wc_social"]) / 3
    resp = sum(s[k] for k in ["resp_scope","resp_auto","resp_rev","resp_dec"]) / 4
    raw  = tc*0.125 + bc*0.125 + effort*0.125 + pc*0.25 + wc*0.125 + resp*0.25
    return {"tc":tc,"bc":bc,"ic":ic,"effort":effort,"mental":mental,"emot":emot,
            "pc":pc,"wc":wc,"resp":resp,"raw":raw,"final":math.floor(raw*10)/10}

def lookup_level(score):
    return min(PAY_STRUCTURE.items(), key=lambda x: abs(x[1]["score"]-score))[0]

# ──────────────────────────────────────────────────────────────────────────────
# SHARED UI HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def page_header(title, subtitle, badge=None):
    b = badge or title.upper()
    st.markdown(f"""
<div class="page-header">
  <div class="page-header-badge">{b}</div>
  <h1 class="page-title">{title}</h1>
  <p class="page-subtitle">{subtitle}</p>
</div>""", unsafe_allow_html=True)

def info_box(text):
    st.markdown(f'<div class="info-panel">{text}</div>', unsafe_allow_html=True)

def score_slider(label, key, hint=None):
    """Persist scores across page navigation.

    Streamlit deletes widget keys (key=) from session_state when the widget is
    not rendered. To survive navigation, we separate:
      - storage key  (e.g. "tc_legal")  — set by init_state(), never a widget key
      - widget key   (e.g. "_w_tc_legal") — used only for the slider DOM element

    On every render we (re)initialise the widget key from the storage key if it
    was cleared, render the slider, then write the result back to the storage key.
    """
    wkey = f"_w_{key}"
    if wkey not in st.session_state:
        st.session_state[wkey] = st.session_state.get(key, 2)
    if hint:
        st.markdown(f'<div class="sub-dim-hint">{hint}</div>', unsafe_allow_html=True)
    val = st.select_slider(label, options=list(range(6)),
                           format_func=lambda x: SCORE_LABELS[x], key=wkey)
    st.session_state[key] = val   # write back to persistent storage key
    return val

def anchor_radio(domain, key, hint, anchors):
    """One card per domain with radio buttons showing full anchor descriptions."""
    wkey = f"_w_{key}"
    if wkey not in st.session_state:
        st.session_state[wkey] = st.session_state.get(key, 2)
    st.markdown(f'<div class="card"><div class="card-title">{domain}</div>', unsafe_allow_html=True)
    if hint:
        st.markdown(f'<div class="sub-dim-hint">{hint}</div>', unsafe_allow_html=True)
    val = st.radio(
        domain,
        options=list(range(6)),
        format_func=lambda x: f"{anchors[x][0]} — {anchors[x][1]}: {anchors[x][2]}",
        key=wkey,
        label_visibility="collapsed",
    )
    st.session_state[key] = val
    st.markdown('</div>', unsafe_allow_html=True)
    return val

def comment_box(key, placeholder="Add comments, justification or context…"):
    """Same separation: _wc_ widget key, persistent storage key."""
    wkey = f"_wc_{key}"
    if wkey not in st.session_state:
        st.session_state[wkey] = st.session_state.get(key, "")
    st.markdown('<div class="comment-header">Comments</div>', unsafe_allow_html=True)
    val = st.text_area("", key=wkey, height=90, placeholder=placeholder,
                       label_visibility="collapsed")
    st.session_state[key] = val

def score_bar_html(score, max_score=5):
    pct = max(0, min(100, score / max_score * 100))
    return f"""<div style="display:flex;align-items:center;gap:10px;">
  <div style="flex:1;background:#EDF2F7;border-radius:4px;height:6px;overflow:hidden;">
    <div style="width:{pct:.0f}%;height:6px;border-radius:4px;background:linear-gradient(90deg,#164A41,#E07B39);"></div>
  </div>
  <span style="font-size:13px;font-weight:600;color:#164A41;min-width:32px;text-align:right;">{score:.2f}</span>
</div>"""

def dimension_row(name, score, weight_label):
    pct = max(0, min(100, score / 5 * 100))
    st.markdown(f"""<div class="dim-row">
  <div class="dim-name">{name}</div>
  <div class="dim-weight">{weight_label}</div>
  <div class="dim-score-bar"><div class="dim-score-bar-bg">
    <div class="dim-score-bar-fill" style="width:{pct:.0f}%"></div>
  </div></div>
  <div class="dim-score-val">{score:.2f}</div>
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PAGES
# ──────────────────────────────────────────────────────────────────────────────
def _text(label, key, **kwargs):
    """Text input with persistent storage key (separate from widget key)."""
    wkey = f"_wi_{key}"
    if wkey not in st.session_state:
        st.session_state[wkey] = st.session_state.get(key, "")
    val = st.text_input(label, key=wkey, **kwargs)
    st.session_state[key] = val
    return val

def _textarea(label, key, **kwargs):
    wkey = f"_wt_{key}"
    if wkey not in st.session_state:
        st.session_state[wkey] = st.session_state.get(key, "")
    val = st.text_area(label, key=wkey, **kwargs)
    st.session_state[key] = val
    return val

def page_job_info():
    page_header("Job Information", "Basic details about the evaluation.", "New Evaluation")
    st.markdown('<div class="card"><div class="card-title">Evaluation Details</div>', unsafe_allow_html=True)
    _text("Employee / Candidate Name", "job_name")
    _text("Evaluator", "evaluator")
    st.date_input("Evaluation Date", key="eval_date")
    st.markdown('</div>', unsafe_allow_html=True)

    info_box("""<strong>How to use this tool</strong><br>
Score each sub-dimension from <strong>0 to 5</strong>. Scores are saved as you go — navigate freely between
pages and your inputs will be retained. The <strong>Results page</strong> shows the final weighted score,
recommended pay level, and full compensation package, with an Excel export.""")

    st.markdown("""<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:4px;">
  <div style="background:#F8FAFD;border:1px solid #E2EAF4;border-radius:10px;padding:14px 16px;">
    <div style="font-size:11px;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:#1A3A5C;">Competency</div>
    <div style="font-size:11px;color:#94A3B8;margin-top:3px;">Technical + Behavioural · 25% weight</div>
  </div>
  <div style="background:#F8FAFD;border:1px solid #E2EAF4;border-radius:10px;padding:14px 16px;">
    <div style="font-size:11px;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:#1A3A5C;">Capital & Responsibility</div>
    <div style="font-size:11px;color:#94A3B8;margin-top:3px;">Professional Capital + Responsibility · 50% weight</div>
  </div>
  <div style="background:#F8FAFD;border:1px solid #E2EAF4;border-radius:10px;padding:14px 16px;">
    <div style="font-size:11px;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:#1A3A5C;">Effort & Context</div>
    <div style="font-size:11px;color:#94A3B8;margin-top:3px;">Effort + Working Conditions · 25% weight</div>
  </div>
</div>""", unsafe_allow_html=True)


TECH_ANCHORS = {
    "Legal / Core competency": {
        "hint": "Solid legal expertise and ability to apply legal reasoning to business and organisational questions.",
        "anchors": [
            (0, "Aptitude",                      "Strong analytical and legal reasoning potential. Understands core legal logic conceptually but cannot yet apply it professionally."),
            (1, "Legal foundation",              "Legally literate consultant — not yet an independent legal advisor. Understands core principles (employment, reward, governance, labour, social security, tax law); interprets standard positions with guidance."),
            (2, "Independent legal professional","Fully functional legal professional. Independently analyses legal questions, translates law into business-relevant advice, and advises on standard scenarios without supervision."),
            (3, "Advanced legal specialist",     "Trusted senior legal-strategic consultant. Handles complex, multi-dimensional questions independently; integrates law with reward strategy and governance; anticipates legal consequences of strategic choices."),
            (4, "Legal authority",               "Legal authority in strategic consultancy context. Defines positions in complex or high-impact situations; shapes legal governance frameworks; acts as reference authority within the practice."),
            (5, "Legal architect / thought leader", "Legal architect of strategic people and reward governance. Develops new methodologies; shapes how law is applied to reward strategy; influences professional or industry thinking."),
        ],
    },
    "Data": {
        "hint": "Data literacy and ability to work with structured analyses and computations.",
        "anchors": [
            (0, "Aptitude",               "Strong quantitative and analytical aptitude. Understands basic data, mathematical, and logical concepts but cannot yet apply them professionally."),
            (1, "Foundational",           "Can perform basic calculations, use simple formulas, translate some business logic into Excel, and follow predefined models. Computation is mechanical and guided."),
            (2, "Independent professional","Can build structured calculation models, perform multi-step computations, check consistency and logic, and apply quantitative reasoning independently. Minimum professional data level."),
            (3, "Advanced professional",  "Can design complex computational models, integrate multiple datasets, handle assumptions and scenarios, and combine computation with analytical judgment. Tools: advanced Excel, Power Query, SQL."),
            (4, "Expert",                 "Can design data and computation architectures, handle statistical or algorithmic complexity, and validate models conceptually. Tools: Python, R, SQL, BI, advanced modelling."),
            (5, "Reference authority",    "Designs or defines advanced computational and analytical methodologies. Influences how data analysis is done across the firm — operates beyond tool-level expertise."),
        ],
    },
    "Strategy": {
        "hint": "Strategic thinking and ability to integrate legal and quantitative insights with strategic considerations.",
        "anchors": [
            (0, "Aptitude",                        "Demonstrates curiosity about how organisations create value. Can follow strategic reasoning but does not yet apply it independently."),
            (1, "Strategy foundation",             "Strategically literate consultant — not yet an independent strategist. Applies standard tools under guidance; communicates strategic concepts clearly."),
            (2, "Independent strategy professional","Conducts structured strategic analyses independently; formulates coherent problem statements; synthesises qualitative and quantitative insights; supports decision-making with well-reasoned recommendations."),
            (3, "Advanced strategy specialist",    "Designs analyses tailored to complex contexts; challenges assumptions; evaluates strategic options with clear trade-off logic; integrates market, organisational, financial, and human factors."),
            (4, "Strategy authority",              "Defines strategic direction for business units or organisations; designs strategic planning and governance processes; advises top decision-makers on long-term implications."),
            (5, "Strategy architect / thought leader", "Develops new strategic concepts or methodologies; influences organisational or industry strategic thinking; integrates strategy with transformation, culture, and governance."),
        ],
    },
    "Leadership": {
        "hint": "Enabling others and the organisation to perform — not hierarchical authority. Requires at least level 2 across the three technical domains.",
        "anchors": [
            (0, "Leadership aptitude",        "No demonstrated leadership yet, but clear leadership potential. Demonstrates openness to responsibility; accepts guidance constructively."),
            (1, "Self-leadership",            "Leads own work through professional discipline and judgment. Takes ownership of own work, quality, and deadlines; demonstrates accountability for own outputs."),
            (2, "Informal expert leadership", "Leads peers through expertise, not authority. Supports peers through content-based problem-solving; shares expertise proactively; builds trust through competence and reliability."),
            (3, "Team leadership",            "Leads delivery by integrating multiple areas of expertise. Leads teams or projects based on subject-matter authority; guides performance through coaching; resolves conflicts using professional judgment."),
            (4, "Organisational leadership",  "Leads the organisation by setting professional direction and standards. Leads multiple teams through professional authority; shapes culture; builds leadership capability in others."),
            (5, "Institutional leadership",   "Leads the institution through vision, credibility, and stewardship. Shapes organisational identity and long-term direction; acts as a moral and professional reference point."),
        ],
    },
    "Transformational": {
        "hint": "Capability to reshape business models, organisations, and systems over time. Requires at least level 2 across the three technical domains.",
        "anchors": [
            (0, "Transformational aptitude",      "Basic capacity to cope with change, not yet independent. Understands that change is inherent to organisations; shows openness to learning and adjustment."),
            (1, "Adaptive professional",          "Can function professionally in a VUCA environment. Operates effectively in changing contexts; adjusts approach as information evolves; maintains performance during transitions."),
            (2, "Independent change operator",    "Independent professional operating in change. Anticipates change impacts on own environment; helps others navigate uncertainty; integrates multiple perspectives during change."),
            (3, "Transformation lead",            "Leads transformation initiatives. Designs and leads change initiatives; translates strategy into transition paths; aligns stakeholders; manages systemic interdependencies."),
            (4, "Strategic transformation leader","Enterprise-level transformation authority. Shapes large-scale transformations; redesigns organisational systems and models; balances stability and change."),
            (5, "System architect",               "Architect of systemic transformation. Redefines how organisations adapt; creates new transformation paradigms; influences professional or industry thinking."),
        ],
    },
}

def page_technical():
    page_header("Technical Competency",
                "Multidisciplinary expertise across five domains · Weight: 12.5%", "Technical")
    info_box("At Stratarius, <strong>leadership belongs to technical capability</strong> — because leadership without expertise has no legitimacy. Score each domain independently; at least one domain should score 0 or 1. <strong>When in doubt, select the lower level.</strong>")

    keys = ["tc_legal", "tc_data", "tc_strategy", "tc_leadership", "tc_transformational"]
    for key, (domain, meta) in zip(keys, TECH_ANCHORS.items()):
        anchor_radio(domain, key, meta["hint"], meta["anchors"])

    tc = sum(st.session_state[k] for k in keys) / 5
    st.markdown(f'<div style="margin:4px 0 16px 0;">{score_bar_html(tc)}</div>', unsafe_allow_html=True)
    st.caption(f"Technical Competency score: **{tc:.2f} / 5** (arithmetic average)")
    comment_box("comment_tc")


def page_behavioural():
    page_header("Behavioural Competency",
                "Interaction complexity, frequency, consequence & conflict · Weight: 12.5%", "Behavioural")
    info_box("The overall BC score uses a <strong>weighted geometric mean</strong> — a very low score on any single dimension significantly reduces the total. This captures that all behavioural capabilities must be sufficiently present.")
    st.markdown('<div class="card"><div class="card-title">Interaction Complexity — 4 Sub-scores</div>', unsafe_allow_html=True)
    st.caption("Rule: 2 or more scores of 5 → IC = 5 | 2 or more scores of 4 → IC = 4 | otherwise: rounded average")
    score_slider("Complexity / ambiguity of the client problem", "bc_ic_cp",
        hint="How complex or ambiguous is the core client problem?")
    score_slider("Complexity / ambiguity of the client system", "bc_ic_cs",
        hint="How complex is the stakeholder system? (number of stakeholders, politics, etc.)")
    score_slider("Team interaction", "bc_ic_team",
        hint="How complex is the required team collaboration?")
    score_slider("Organizational interaction", "bc_ic_org",
        hint="How complex is the interaction with the broader organization?")
    ic = calc_ic([st.session_state[k] for k in ["bc_ic_cp","bc_ic_cs","bc_ic_team","bc_ic_org"]])
    st.markdown(f'<div class="computed-chip"><span style="color:#94A3B8;">Interaction Complexity (computed):</span> <strong style="color:#E07B39;font-size:16px;">{ic}</strong> / 5</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Other Behavioural Dimensions</div>', unsafe_allow_html=True)
    score_slider("Frequency of complex interactions", "bc_freq", hint="Weight: 25% within BC")
    score_slider("Consequence of interaction quality", "bc_cons", hint="Weight: 25% within BC")
    score_slider("Conflict handling and managing resistance", "bc_conf", hint="Weight: 20% within BC")
    st.markdown('</div>', unsafe_allow_html=True)
    ic_n = ic/5; fr_n = st.session_state["bc_freq"]/5
    co_n = st.session_state["bc_cons"]/5; cf_n = st.session_state["bc_conf"]/5
    bc = round((ic_n**0.3*fr_n**0.25*co_n**0.25*cf_n**0.2)*5,2) if all(v>0 for v in [ic_n,fr_n,co_n,cf_n]) else 0.0
    st.markdown(f'<div style="margin:4px 0 16px 0;">{score_bar_html(bc)}</div>', unsafe_allow_html=True)
    st.caption(f"Behavioural Competency score: **{bc:.2f} / 5** (geometric mean × 5)")
    comment_box("comment_bc")


def page_effort():
    page_header("Effort",
                "Mental burden (50%) + Emotional burden (50%) · Weight: 12.5%", "Effort")
    info_box("Effort recognizes the <strong>cognitive and emotional demands</strong> of the role. Both mental and emotional effort contribute equally (50% each).")
    st.markdown('<div class="card"><div class="card-title">Mental Effort</div>', unsafe_allow_html=True)
    score_slider("Concentration and focus required", "ef_conc", hint="Level of sustained attention required (w: 15%)")
    score_slider("Complexity of problem-solving", "ef_prob", hint="How complex are the problems to solve? (w: 25%)")
    score_slider("Amount of information to process and retain", "ef_info", hint="Volume and complexity of information (w: 25%)")
    score_slider("Multitasking demands", "ef_multi", hint="Simultaneous task management requirements (w: 15%)")
    score_slider("Switching roles", "ef_switch", hint="Frequency of switching between different modes or roles (w: 20%)")
    mental = (sum(st.session_state[k] for k in ["ef_conc","ef_prob","ef_info","ef_multi","ef_switch"]) / 5) * 0.5
    st.markdown(f'<div style="margin:4px 0 4px 0;">{score_bar_html(mental, max_score=2.5)}</div>', unsafe_allow_html=True)
    st.caption(f"Mental effort contribution: **{mental:.2f}** (avg × 0.5)")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Emotional Effort</div>', unsafe_allow_html=True)
    score_slider("Regulation of own emotions", "ef_own", hint="Managing personal emotional reactions under pressure")
    score_slider("Managing others' emotions", "ef_oth", hint="Handling the emotional states of clients, colleagues, stakeholders")
    score_slider("Dealing with conflict, complaints, distress", "ef_conf", hint="Frequency and intensity of difficult emotional interactions")
    score_slider("Maintaining professional demeanor under pressure", "ef_press", hint="Composure in high-stakes or high-pressure situations")
    emot = (sum(st.session_state[k] for k in ["ef_own","ef_oth","ef_conf","ef_press"]) / 4) * 0.5
    st.markdown(f'<div style="margin:4px 0 4px 0;">{score_bar_html(emot, max_score=2.5)}</div>', unsafe_allow_html=True)
    st.caption(f"Emotional effort contribution: **{emot:.2f}** (avg × 0.5)")
    st.markdown('</div>', unsafe_allow_html=True)
    effort = mental + emot
    st.markdown(f'<div style="margin:4px 0 16px 0;">{score_bar_html(effort)}</div>', unsafe_allow_html=True)
    st.caption(f"Total Effort score: **{effort:.2f} / 5**")
    comment_box("comment_ef")


def page_professional():
    page_header("Professional Capital",
                "Trust, credibility and accumulated capital · Weight: 25%", "Professional Capital")
    info_box("Professional Capital is one of the two <strong>highest-weighted dimensions (25%)</strong> because Stratarius is a customer-intimate consultancy where trust and credibility are absolutely core.")
    st.markdown('<div class="card"><div class="card-title">Three Dimensions of Capital</div>', unsafe_allow_html=True)
    score_slider("Professional credibility", "pc_cred",
        hint="Level at which advice is accepted — from emerging credibility to recognised authority (w: 1/3)")
    score_slider("Relational capital", "pc_rel",
        hint="Strength of professional relationships that can be activated for Stratarius (w: 1/3)")
    score_slider("Organizational capital", "pc_org",
        hint="Institutional knowledge, client dependency, key-person continuity value (w: 1/3)")
    st.markdown('</div>', unsafe_allow_html=True)
    with st.expander("Score anchors"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""**Professional Credibility**
| Score | Meaning |
|--|--|
| 1–2 | Advice needs validation or escalation |
| 3 | Generally accepted, occasional escalation |
| 4 | Normally accepted without escalation |
| 5 | Authority — rarely challenged |""")
        with col2:
            st.markdown("""**Organizational Capital**
| Score | Meaning |
|--|--|
| 0–1 | No continuity accumulated yet |
| 2–3 | Some institutional knowledge |
| 4 | High know-how, key relationships |
| 5 | Critical continuity, high key-person value |""")
    pc = sum(st.session_state[k] for k in ["pc_cred","pc_rel","pc_org"]) / 3
    st.markdown(f'<div style="margin:4px 0 16px 0;">{score_bar_html(pc)}</div>', unsafe_allow_html=True)
    st.caption(f"Professional Capital score: **{pc:.2f} / 5** (arithmetic average)")
    comment_box("comment_pc")


def page_working():
    page_header("Working Conditions",
                "Schedule, travel and organizational context · Weight: 12.5%", "Working Conditions")
    info_box("Working conditions recognize the <strong>context</strong> in which the role operates. Higher scores indicate more demanding or less favourable conditions.")
    st.markdown('<div class="card"><div class="card-title">Three Context Dimensions</div>', unsafe_allow_html=True)
    score_slider("Schedule demands", "wc_sched",
        hint="Irregular hours, on-call requirements, schedule pressure (w: 33%)")
    score_slider("Travel demands", "wc_travel",
        hint="Frequency, duration and disruption of required travel (w: 33%)")
    score_slider("Social and organizational environment", "wc_social",
        hint="Level of organizational support vs. startup-like self-reliance (w: 33%)")
    st.markdown('</div>', unsafe_allow_html=True)
    wc = sum(st.session_state[k] for k in ["wc_sched","wc_travel","wc_social"]) / 3
    st.markdown(f'<div style="margin:4px 0 16px 0;">{score_bar_html(wc)}</div>', unsafe_allow_html=True)
    st.caption(f"Working Conditions score: **{wc:.2f} / 5** (arithmetic average)")
    comment_box("comment_wc")


def page_responsibility():
    page_header("Level of Responsibility",
                "Scope, autonomy, risk and decision complexity · Weight: 25%", "Responsibility")
    info_box("Responsibility is the other highest-weighted dimension (25%) — Stratarius values <strong>accountability</strong> and the ability to own outcomes independently.")
    st.markdown('<div class="card"><div class="card-title">Four Responsibility Dimensions</div>', unsafe_allow_html=True)
    score_slider("Scope of impact", "resp_scope",
        hint="From individual task accountability to broad organizational or client-wide impact (w: 25%)")
    score_slider("Autonomy and decision-making authority", "resp_auto",
        hint="From guided execution within defined boundaries to full strategic autonomy (w: 25%)")
    score_slider("Reversibility and risk", "resp_rev",
        hint="Degree to which decisions are hard to reverse or carry significant risk (w: 25%)")
    score_slider("Decision complexity and frequency", "resp_dec",
        hint="How complex and frequent are the decisions the role must take? (w: 25%)")
    st.markdown('</div>', unsafe_allow_html=True)
    with st.expander("Score anchors"):
        st.markdown("""
| Score | Description |
|--|--|
| **1** | Own tasks only; guided execution; escalates regularly |
| **2** | Accountable for analyses and deliverables; exercises judgment within defined bounds |
| **3** | Accountable for project outcomes; autonomous decisions on client work |
| **4** | Client-level and organizational impact; owns project outcomes |
| **5** | Full strategic ownership; shapes direction; decisions rarely reversed |""")
    resp = sum(st.session_state[k] for k in ["resp_scope","resp_auto","resp_rev","resp_dec"]) / 4
    st.markdown(f'<div style="margin:4px 0 16px 0;">{score_bar_html(resp)}</div>', unsafe_allow_html=True)
    st.caption(f"Responsibility score: **{resp:.2f} / 5** (arithmetic average)")
    comment_box("comment_resp")


def page_results():
    page_header("Results & Pay Proposal",
                "Final score, recommended pay level and full compensation package", "Results")
    sc = calculate_scores()
    cat = lookup_level(sc["final"])
    pay = PAY_STRUCTURE[cat]

    # Top KPI row
    kpis = [("Final Score", f"{sc['final']:.1f}", True),
            ("Raw Score",   f"{sc['raw']:.3f}", False),
            ("Pay Level",   cat, False),
            ("Base Salary", f"€{pay['salary']:,.0f}/mo", False)]
    cols = st.columns(4)
    for col, (label, val, hi) in zip(cols, kpis):
        extra = "metric-highlight" if hi else ""
        col.markdown(f"""<div class="metric-card {extra}">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{val}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="card"><div class="card-title">Score Breakdown</div>', unsafe_allow_html=True)
        dims = [
            ("Technical Competency",    sc["tc"],     "12.5%"),
            ("Behavioural Competency",  sc["bc"],     "12.5%"),
            ("Effort",                  sc["effort"], "12.5%"),
            ("Professional Capital",    sc["pc"],     "25%"),
            ("Working Conditions",      sc["wc"],     "12.5%"),
            ("Level of Responsibility", sc["resp"],   "25%"),
        ]
        for name, score, wt in dims:
            dimension_row(name, score, wt)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        annual = pay["salary"] * 13.92
        st.markdown(f"""<div class="card">
  <div class="card-title">Pay Level</div>
  <div style="text-align:center;margin-bottom:16px;">
    <div style="font-size:10px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#94A3B8;margin-bottom:6px;">Category</div>
    <div class="pay-level-badge">{cat}</div>
    <div style="font-size:11px;color:#94A3B8;margin-top:6px;">Score threshold: {pay['score']}</div>
  </div>
  <table class="comp-table">
    <tr class="comp-hi"><td>Base monthly (gross)</td><td>€ {pay['salary']:,.2f}</td></tr>
    <tr><td>Annual (× 13.92)</td><td>€ {annual:,.0f}</td></tr>
    <tr class="comp-hi"><td>Mobility budget</td><td>€ {pay['mobility']:,} /mo</td></tr>
    <tr><td>Home work allowance</td><td>€ 150 /mo</td></tr>
    <tr><td>Meal vouchers</td><td>€ 10 / day</td></tr>
    <tr><td>Ecovouchers</td><td>€ 250 /yr</td></tr>
    <tr><td>Yearly premium</td><td>€ 330.84</td></tr>
    <tr><td>Collective bonus</td><td>up to €3,700 net/yr</td></tr>
    <tr><td>Paid days off</td><td>45 days /yr</td></tr>
  </table>
</div>""", unsafe_allow_html=True)

    with st.expander("Detailed weighted calculation"):
        weights = [0.125, 0.125, 0.125, 0.25, 0.125, 0.25]
        scores_vals = [sc["tc"],sc["bc"],sc["effort"],sc["pc"],sc["wc"],sc["resp"]]
        dim_names = ["Technical Competency","Behavioural Competency","Effort",
                     "Professional Capital","Working Conditions","Level of Responsibility"]
        rows = [{"Dimension":n,"Score":round(s,3),"Weight":w,"Weighted":round(s*w,4)}
                for n,s,w in zip(dim_names,scores_vals,weights)]
        rows.append({"Dimension":"TOTAL","Score":"","Weight":sum(weights),"Weighted":round(sc["raw"],4)})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    with st.expander("Full pay structure — all levels"):
        ps = [{"Level":lvl,"Score":d["score"],"Gross /mo":f"€{d['salary']:,.2f}",
               "Annual (×13.92)":f"€{d['salary']*13.92:,.0f}",
               "Mobility":f"€{d['mobility']:,}",
               "Selected": "Yes" if lvl==cat else ""}
              for lvl,d in PAY_STRUCTURE.items()]
        st.dataframe(pd.DataFrame(ps), hide_index=True, use_container_width=True)

    st.markdown('<hr style="border:none;border-top:1px solid #EDF2F7;margin:20px 0;">', unsafe_allow_html=True)
    comment_box("overall_comments", "Overall observations and rationale for the proposed pay level…")
    st.markdown('<hr style="border:none;border-top:1px solid #EDF2F7;margin:20px 0;">', unsafe_allow_html=True)

    st.markdown('<div class="card-title" style="padding-bottom:10px;border-bottom:1px solid #EDF2F7;margin-bottom:14px;">Export</div>', unsafe_allow_html=True)
    if st.button("Generate Excel Report", type="primary", use_container_width=True):
        buf = export_excel(sc)
        candidate = st.session_state.get("job_name","evaluation").replace(" ","_")
        st.download_button("Download Excel Report", data=buf,
                           file_name=f"stratarius_job_evaluation_{candidate}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)


def page_info():
    page_header("Reward Strategy", "Reference information from the Stratarius Reward Strategy document", "Reference")
    tab1, tab2, tab3, tab4 = st.tabs(["Philosophy", "Scoring Logic", "Profile Examples", "Total Package"])

    with tab1:
        st.markdown("""
> *"At Stratarius we primarily value (and therefore reward) technical and behavioural competence,
> professional credibility and responsibility, while recognizing effort and working conditions as
> important but secondary job factors."*

| Category | Message |
|--|--|
| **Competency** | We value capability — technical and behavioural equally |
| **Professional Capital** | We value trust and credibility |
| **Responsibility** | We value accountability |
| **Effort** | We recognize burden |
| **Working Conditions** | We recognize context |

### Pay Levels

Approximately 41 pay levels across 5 categories: **A5–A9 · B0–B9 · C0–C9 · D0–D9 · E0–E5**

### Governance

The pay level is based on the individual's capabilities *(looking back)* and the job demands *(looking forward)*. The process is **fully transparent** and the subject of an open discussion. The pay level is the outcome of a **principled negotiation** — non-negotiable on outcome, but the principles are subject to dialogue.
""")

    with tab2:
        st.markdown("""
### Dimension Weights

| Dimension | Weight | Why |
|--|--|--|
| Technical Competency | 12.5% | Core capability |
| Behavioural Competency | 12.5% | Core capability — equal to technical |
| **Professional Capital** | **25%** | Trust and credibility — most critical |
| **Level of Responsibility** | **25%** | Accountability — most critical |
| Effort | 12.5% | Recognized but secondary |
| Working Conditions | 12.5% | Context — recognized but secondary |

### Scoring Methods

- **Technical Competency:** Arithmetic average of 5 domains *(minimum 0 or 1 in at least one domain)*
- **Behavioural Competency:** Weighted geometric mean — `(IC^0.3 × Freq^0.25 × Cons^0.25 × Conf^0.2) × 5`
- **Interaction Complexity rule:** 2+ scores of 5 → IC = 5 | 2+ scores of 4 → IC = 4 | else: rounded average
- **Effort:** `AVERAGE(mental subs) × 0.5 + AVERAGE(emotional subs) × 0.5`
- **All other dimensions:** Arithmetic average
- **Final score:** Weighted sum → rounded *down* to 1 decimal
""")

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class="card">
<div class="card-title">Profile — Level B6</div>

**HR legal expert · approx. 5 years experience**

*Technical:* Solid legal expertise, data literate, integrates legal insight with strategy, supports peers

*Behavioural:* Ambiguous client situations (mainly problem, less system); manages disagreement

*Professional Capital:* Emerging credibility — advice still requires some validation

*Responsibility:* Accountable for own analyses; exercises judgment within defined boundaries

**B6 — €4,489.80 gross / month**
</div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class="card">
<div class="card-title">Profile — Level C4</div>

**HR legal expert · approx. 10 years experience**

*Technical:* HR legal authority; shapes legal frameworks; leads teams based on subject-matter expertise

*Behavioural:* Largely autonomous in ambiguous situations (both problem and system)

*Professional Capital:* Strong credibility — advice normally accepted without escalation

*Responsibility:* Client-level and organizational impact; autonomous decisions; owns project outcomes

**C4 — €6,633.47 gross / month**
</div>""", unsafe_allow_html=True)

    with tab4:
        st.markdown("""
### Total Compensation Package

| Component | Details |
|--|--|
| Base monthly salary | Paid 13.92× per year |
| Mobility budget / company car | A: €780 · B: €930 · C: €1,080 · D: €1,230 · E: €1,380 /month |
| Meal vouchers | €10 / worked day (employer €8.91, employee €1.09) |
| Home work allowance | €150 / month (min. 1 day/week from home) |
| Ecovouchers | €250 / year |
| Yearly premium | €330.84 (2026) |
| Supplementary pension | % of 12 × monthly base salary |
| Guaranteed income | Up to 100% regular net income (illness/accident) |
| Hospitalisation insurance | Option to affiliate family members |
| Collective bonus | Up to €3,700 net / year (FTE) |
| Share purchase | Possibility to purchase Stratarius shares |
| Paid days off | 45 days / year (FTE) |

### Professional and Eudaimonic Well-being

MacBook Air / Dell XPS · curved screens · ergonomic setup at office and home · LinkedIn Premium ·
networking events (Belgium and abroad) · workation · formal education · personal brand opportunities ·
room for research and experimentation
""")


# ──────────────────────────────────────────────────────────────────────────────
# EXCEL EXPORT
# ──────────────────────────────────────────────────────────────────────────────
def export_excel(sc):
    s = st.session_state
    wb = Workbook()
    navy="164A41"; orange="E07B39"; light="EFF7F4"; mid="1D5C4E"
    thin = Side(style="thin", color="D1DDED")
    bdr  = Border(left=thin, right=thin, top=thin, bottom=thin)
    ctr  = Alignment(horizontal="center", vertical="center")
    wrap = Alignment(wrap_text=True, vertical="top")

    def hdr(ws, r, c, v, fg=navy, size=11):
        cell = ws.cell(r, c, v)
        cell.fill = PatternFill("solid", fgColor=fg)
        cell.font = Font(color="FFFFFF", bold=True, size=size)
        cell.alignment = ctr; cell.border = bdr; return cell

    def dat(ws, r, c, v, bold=False, bg=None, align=None):
        cell = ws.cell(r, c, v)
        if bold:  cell.font  = Font(bold=True, size=10)
        if bg:    cell.fill  = PatternFill("solid", fgColor=bg)
        cell.alignment = align or wrap; cell.border = bdr; return cell

    # Sheet 1: Job Info
    ws1 = wb.active; ws1.title = "Job Info"
    ws1.column_dimensions["A"].width = 28; ws1.column_dimensions["B"].width = 44
    ws1.row_dimensions[1].height = 30
    hdr(ws1,1,1,"JOB ARCHITECTURE EVALUATION — STRATARIUS",navy,13); ws1.merge_cells("A1:B1")
    for i,(k,v) in enumerate([
        ("Employee / Candidate", s.get("job_name","")),
        ("Evaluator", s.get("evaluator","")),
        ("Evaluation Date", str(s.get("eval_date",""))),
    ], start=2):
        dat(ws1,i,1,k,bold=True,bg=light); dat(ws1,i,2,v)

    # Sheet 2: Scoring Details
    ws2 = wb.create_sheet("Scoring Details")
    ws2.column_dimensions["A"].width=42; ws2.column_dimensions["B"].width=10
    ws2.column_dimensions["C"].width=12; ws2.column_dimensions["D"].width=12; ws2.column_dimensions["E"].width=50
    hdr(ws2,1,1,"Sub-dimension"); hdr(ws2,1,2,"Score"); hdr(ws2,1,3,"Weight"); hdr(ws2,1,4,"Dim Score"); hdr(ws2,1,5,"Comments")
    row = [2]

    def add_dim(name, score, wt, comment=""):
        r = row[0]
        hdr(ws2,r,1,name,mid); dat(ws2,r,2,"")
        dat(ws2,r,3,wt,align=ctr); dat(ws2,r,4,round(score,3),bold=True,align=ctr); dat(ws2,r,5,comment,align=wrap)
        row[0] += 1

    def add_sub(name, score, wt=""):
        r = row[0]
        dat(ws2,r,1,f"    {name}",bg=light); dat(ws2,r,2,score,align=ctr)
        dat(ws2,r,3,wt,align=ctr); dat(ws2,r,4,""); dat(ws2,r,5,"")
        row[0] += 1

    add_dim("1. Technical Competency", sc["tc"], "12.5%", s.get("comment_tc",""))
    for k,lbl,w in [("tc_legal","Legal / Core","20%"),("tc_data","Data","20%"),("tc_strategy","Strategy","20%"),("tc_leadership","Leadership","20%"),("tc_transformational","Transformational","20%")]:
        add_sub(lbl, s.get(k,2), w)

    add_dim("2. Behavioural Competency", sc["bc"], "12.5%", s.get("comment_bc",""))
    for k,lbl in [("bc_ic_cp","IC - Client problem"),("bc_ic_cs","IC - Client system"),("bc_ic_team","IC - Team interaction"),("bc_ic_org","IC - Org interaction")]:
        add_sub(lbl, s.get(k,2))
    add_sub(f"Interaction Complexity (computed: {sc['ic']})", sc['ic'], "30%")
    for k,lbl,w in [("bc_freq","Frequency","25%"),("bc_cons","Consequence","25%"),("bc_conf","Conflict","20%")]:
        add_sub(lbl, s.get(k,2), w)

    add_dim("3. Effort", sc["effort"], "12.5%", s.get("comment_ef",""))
    for k,lbl in [("ef_conc","Mental: Concentration"),("ef_prob","Mental: Problem-solving"),("ef_info","Mental: Information"),("ef_multi","Mental: Multitasking"),("ef_switch","Mental: Role switching")]:
        add_sub(lbl, s.get(k,2))
    for k,lbl in [("ef_own","Emotional: Own emotions"),("ef_oth","Emotional: Others emotions"),("ef_conf","Emotional: Conflict"),("ef_press","Emotional: Pressure")]:
        add_sub(lbl, s.get(k,2))

    add_dim("4. Professional Capital", sc["pc"], "25%", s.get("comment_pc",""))
    for k,lbl in [("pc_cred","Professional credibility"),("pc_rel","Relational capital"),("pc_org","Organizational capital")]:
        add_sub(lbl, s.get(k,2), "1/3")

    add_dim("5. Working Conditions", sc["wc"], "12.5%", s.get("comment_wc",""))
    for k,lbl in [("wc_sched","Schedule demands"),("wc_travel","Travel demands"),("wc_social","Social environment")]:
        add_sub(lbl, s.get(k,2), "33%")

    add_dim("6. Level of Responsibility", sc["resp"], "25%", s.get("comment_resp",""))
    for k,lbl in [("resp_scope","Scope of impact"),("resp_auto","Autonomy and decision authority"),("resp_rev","Reversibility and risk"),("resp_dec","Decision complexity")]:
        add_sub(lbl, s.get(k,2), "25%")

    # Sheet 3: Results
    ws3 = wb.create_sheet("Results & Pay Proposal")
    ws3.column_dimensions["A"].width=36; ws3.column_dimensions["B"].width=24; ws3.column_dimensions["C"].width=18
    ws3.row_dimensions[1].height=30
    hdr(ws3,1,1,"RESULTS & PAY PROPOSAL — STRATARIUS",navy,13); ws3.merge_cells("A1:C1")
    r=2; hdr(ws3,r,1,"Dimension",mid); hdr(ws3,r,2,"Score",mid); hdr(ws3,r,3,"Weight",mid); r+=1
    for name,score,wt in [("Technical Competency",sc["tc"],"12.5%"),("Behavioural Competency",sc["bc"],"12.5%"),
                           ("Effort",sc["effort"],"12.5%"),("Professional Capital",sc["pc"],"25%"),
                           ("Working Conditions",sc["wc"],"12.5%"),("Level of Responsibility",sc["resp"],"25%")]:
        dat(ws3,r,1,name); dat(ws3,r,2,round(score,3),align=ctr); dat(ws3,r,3,wt,align=ctr); r+=1
    dat(ws3,r,1,"Raw Final Score",bold=True,bg=light); dat(ws3,r,2,round(sc["raw"],4),bold=True,align=ctr); dat(ws3,r,3,"",bg=light); r+=1
    dat(ws3,r,1,"FINAL SCORE (rounded down)",bold=True)
    c2=ws3.cell(r,2,sc["final"]); c2.font=Font(bold=True,size=14,color=orange); c2.fill=PatternFill("solid",fgColor="FFF3E8"); c2.border=bdr; c2.alignment=ctr
    dat(ws3,r,3,""); r+=2
    cat = lookup_level(sc["final"]); pay = PAY_STRUCTURE[cat]
    hdr(ws3,r,1,"PAY PROPOSAL",mid); ws3.merge_cells(f"A{r}:C{r}"); r+=1
    for label,value in [
        ("Pay Level", cat), ("Base Monthly Salary (gross)", f"€ {pay['salary']:,.2f}"),
        ("Annual Salary (x 13.92)", f"€ {pay['salary']*13.92:,.2f}"),
        ("Mobility Budget", f"€ {pay['mobility']:,} / month"), ("Home Work Allowance", "€ 150 / month"),
        ("Meal Vouchers", "€ 10 / worked day"), ("Ecovouchers", "€ 250 / year"),
        ("Yearly Premium (2026)", "€ 330.84"), ("Collective Bonus", "Up to €3,700 net / year (FTE)"),
        ("Paid Days Off", "45 days / year (FTE)"), ("Overall Comments", s.get("overall_comments","")),
    ]:
        dat(ws3,r,1,label,bold=True,bg=light); c2=ws3.cell(r,2,value); c2.border=bdr; c2.alignment=wrap; ws3.merge_cells(f"B{r}:C{r}"); r+=1

    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    sc = calculate_scores()
    cat = lookup_level(sc["final"])
    pay = PAY_STRUCTURE[cat]
    pct = int(min(sc["final"] / 4.5 * 100, 100))
    current = st.session_state.get("_page", "job_info")

    with st.sidebar:
        st.markdown(f"""<div class="sidebar-logo">
  <img src="https://cdn.prod.website-files.com/673dbfdf2f3d713ccf63b52c/6751dac6302746797e66f059_Artboard%201.webp"
       onerror="this.style.display='none'" alt="Stratarius">
  <div class="sidebar-brand">Job Architecture Tool</div>
</div>""", unsafe_allow_html=True)

        for label, page_id in PAGES:
            is_active = (current == page_id)
            if st.button(label, key=f"nav_{page_id}",
                         use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state["_page"] = page_id
                st.rerun()

        st.markdown(f"""<div class="score-preview">
  <div class="score-preview-label">Live Score</div>
  <div class="score-big">{sc['final']:.1f}</div>
  <div class="score-level">{cat}</div>
  <div class="score-salary">€{pay['salary']:,.0f} / month gross</div>
  <div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%"></div></div>
</div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Job Architecture Scoring — Stratarius",
        page_icon="S",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(STYLES, unsafe_allow_html=True)
    init_state()  # ← all defaults set once; widgets use key= only, no value= override

    render_sidebar()

    dispatch = {
        "job_info":       page_job_info,
        "technical":      page_technical,
        "behavioural":    page_behavioural,
        "effort":         page_effort,
        "professional":   page_professional,
        "working":        page_working,
        "responsibility": page_responsibility,
        "results":        page_results,
        "info":           page_info,
    }
    dispatch.get(st.session_state["_page"], page_job_info)()


if __name__ == "__main__":
    main()
