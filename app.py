import streamlit as st
import pandas as pd
import numpy as np
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import math

# ──────────────────────────────────────────────────────────────────────────────
# PAY STRUCTURE DATA
# ──────────────────────────────────────────────────────────────────────────────
PAY_STRUCTURE = {
    "A5": {"score": 0.5, "salary": 2625.09, "mobility": 780, "home_allowance": 150},
    "A6": {"score": 0.6, "salary": 2756.35, "mobility": 780, "home_allowance": 150},
    "A7": {"score": 0.7, "salary": 2894.16, "mobility": 780, "home_allowance": 150},
    "A8": {"score": 0.8, "salary": 3038.87, "mobility": 780, "home_allowance": 150},
    "A9": {"score": 0.9, "salary": 3190.81, "mobility": 780, "home_allowance": 150},
    "B0": {"score": 1.0, "salary": 3350.35, "mobility": 930, "home_allowance": 150},
    "B1": {"score": 1.1, "salary": 3517.87, "mobility": 930, "home_allowance": 150},
    "B2": {"score": 1.2, "salary": 3693.77, "mobility": 930, "home_allowance": 150},
    "B3": {"score": 1.3, "salary": 3878.45, "mobility": 930, "home_allowance": 150},
    "B4": {"score": 1.4, "salary": 4072.38, "mobility": 930, "home_allowance": 150},
    "B5": {"score": 1.5, "salary": 4276.00, "mobility": 930, "home_allowance": 150},
    "B6": {"score": 1.6, "salary": 4489.80, "mobility": 930, "home_allowance": 150},
    "B7": {"score": 1.7, "salary": 4714.29, "mobility": 930, "home_allowance": 150},
    "B8": {"score": 1.8, "salary": 4950.00, "mobility": 930, "home_allowance": 150},
    "B9": {"score": 1.9, "salary": 5197.50, "mobility": 930, "home_allowance": 150},
    "C0": {"score": 2.0, "salary": 5457.38, "mobility": 1080, "home_allowance": 150},
    "C1": {"score": 2.1, "salary": 5730.24, "mobility": 1080, "home_allowance": 150},
    "C2": {"score": 2.2, "salary": 6016.76, "mobility": 1080, "home_allowance": 150},
    "C3": {"score": 2.3, "salary": 6317.59, "mobility": 1080, "home_allowance": 150},
    "C4": {"score": 2.4, "salary": 6633.47, "mobility": 1080, "home_allowance": 150},
    "C5": {"score": 2.5, "salary": 6965.15, "mobility": 1080, "home_allowance": 150},
    "C6": {"score": 2.6, "salary": 7243.75, "mobility": 1080, "home_allowance": 150},
    "C7": {"score": 2.7, "salary": 7533.50, "mobility": 1080, "home_allowance": 150},
    "C8": {"score": 2.8, "salary": 7834.84, "mobility": 1080, "home_allowance": 150},
    "C9": {"score": 2.9, "salary": 8148.24, "mobility": 1080, "home_allowance": 150},
    "D0": {"score": 3.0, "salary": 8474.17, "mobility": 1230, "home_allowance": 150},
    "D1": {"score": 3.1, "salary": 8813.13, "mobility": 1230, "home_allowance": 150},
    "D2": {"score": 3.2, "salary": 9165.66, "mobility": 1230, "home_allowance": 150},
    "D3": {"score": 3.3, "salary": 9532.28, "mobility": 1230, "home_allowance": 150},
    "D4": {"score": 3.4, "salary": 9913.58, "mobility": 1230, "home_allowance": 150},
    "D5": {"score": 3.5, "salary": 10310.12, "mobility": 1230, "home_allowance": 150},
    "D6": {"score": 3.6, "salary": 10722.52, "mobility": 1230, "home_allowance": 150},
    "D7": {"score": 3.7, "salary": 11151.42, "mobility": 1230, "home_allowance": 150},
    "D8": {"score": 3.8, "salary": 11597.48, "mobility": 1230, "home_allowance": 150},
    "D9": {"score": 3.9, "salary": 12061.38, "mobility": 1230, "home_allowance": 150},
    "E0": {"score": 4.0, "salary": 12543.84, "mobility": 1380, "home_allowance": 150},
    "E1": {"score": 4.1, "salary": 13045.59, "mobility": 1380, "home_allowance": 150},
    "E2": {"score": 4.2, "salary": 13567.41, "mobility": 1380, "home_allowance": 150},
    "E3": {"score": 4.3, "salary": 14110.11, "mobility": 1380, "home_allowance": 150},
    "E4": {"score": 4.4, "salary": 14674.51, "mobility": 1380, "home_allowance": 150},
    "E5": {"score": 4.5, "salary": 15261.49, "mobility": 1380, "home_allowance": 150},
}

SCORE_LABELS = {
    0: "0 – Not present / Not applicable",
    1: "1 – Basic / Entry level",
    2: "2 – Developing / Moderate",
    3: "3 – Proficient / Solid",
    4: "4 – Advanced / Strong",
    5: "5 – Expert / Exceptional",
}

# ──────────────────────────────────────────────────────────────────────────────
# SCORING CALCULATION
# ──────────────────────────────────────────────────────────────────────────────
def calculate_interaction_complexity(sub_scores):
    """IC rule: ≥2 scores of 5 → 5; ≥2 scores of 4 → 4; else rounded average."""
    if sub_scores.count(5) >= 2:
        return 5
    elif sub_scores.count(4) >= 2:
        return 4
    else:
        return round(sum(sub_scores) / len(sub_scores))

def calculate_scores():
    s = st.session_state

    # ── Technical Competency ──
    tc_scores = [
        s.get("tc_legal", 2),
        s.get("tc_data", 2),
        s.get("tc_strategy", 2),
        s.get("tc_leadership", 2),
        s.get("tc_transformational", 2),
    ]
    tc_score = sum(tc_scores) / len(tc_scores)

    # ── Behavioural Competency ──
    ic_subs = [
        s.get("bc_ic_client_problem", 2),
        s.get("bc_ic_client_system", 2),
        s.get("bc_ic_team", 2),
        s.get("bc_ic_org", 2),
    ]
    ic = calculate_interaction_complexity(ic_subs)
    freq = s.get("bc_frequency", 2)
    cons = s.get("bc_consequence", 2)
    conf = s.get("bc_conflict", 2)

    # Geometric mean (weighted) × 5
    ic_n = ic / 5
    freq_n = freq / 5
    cons_n = cons / 5
    conf_n = conf / 5
    if all(v > 0 for v in [ic_n, freq_n, cons_n, conf_n]):
        bc_score = round((ic_n**0.3 * freq_n**0.25 * cons_n**0.25 * conf_n**0.2) * 5, 2)
    else:
        bc_score = 0.0

    # ── Effort ──
    mental_subs = [
        s.get("ef_concentration", 2),
        s.get("ef_complexity", 2),
        s.get("ef_information", 2),
        s.get("ef_multitasking", 2),
        s.get("ef_switching", 2),
    ]
    emotional_subs = [
        s.get("ef_own_emotions", 2),
        s.get("ef_others_emotions", 2),
        s.get("ef_conflict", 2),
        s.get("ef_pressure", 2),
    ]
    mental_score = (sum(mental_subs) / len(mental_subs)) * 0.5
    emotional_score = (sum(emotional_subs) / len(emotional_subs)) * 0.5
    effort_score = mental_score + emotional_score

    # ── Professional Capital ──
    pc_scores = [
        s.get("pc_credibility", 2),
        s.get("pc_relational", 2),
        s.get("pc_organizational", 2),
    ]
    pc_score = sum(pc_scores) / len(pc_scores)

    # ── Working Conditions ──
    wc_scores = [
        s.get("wc_schedule", 2),
        s.get("wc_travel", 2),
        s.get("wc_social", 2),
    ]
    wc_score = sum(wc_scores) / len(wc_scores)

    # ── Level of Responsibility ──
    resp_scores = [
        s.get("resp_scope", 2),
        s.get("resp_autonomy", 2),
        s.get("resp_reversibility", 2),
        s.get("resp_decision", 2),
    ]
    resp_score = sum(resp_scores) / len(resp_scores)

    # ── Final Weighted Score ──
    final = (
        tc_score   * 0.125 +
        bc_score   * 0.125 +
        effort_score * 0.125 +
        pc_score   * 0.25 +
        wc_score   * 0.125 +
        resp_score * 0.25
    )
    final_rounded = math.floor(final * 10) / 10  # ROUNDDOWN to 1 decimal

    return {
        "tc_score": tc_score,
        "bc_score": bc_score,
        "bc_ic": ic,
        "effort_score": effort_score,
        "mental_score": mental_score,
        "emotional_score": emotional_score,
        "pc_score": pc_score,
        "wc_score": wc_score,
        "resp_score": resp_score,
        "final": final,
        "final_rounded": final_rounded,
    }

def lookup_pay_level(final_score):
    """Return the pay level category for a given final score."""
    best_cat = None
    best_diff = float("inf")
    for cat, data in PAY_STRUCTURE.items():
        diff = abs(data["score"] - final_score)
        if diff < best_diff:
            best_diff = diff
            best_cat = cat
    return best_cat

# ──────────────────────────────────────────────────────────────────────────────
# EXCEL EXPORT
# ──────────────────────────────────────────────────────────────────────────────
def export_to_excel(scores):
    s = st.session_state
    wb = Workbook()

    # ── Styling helpers ──
    header_fill = PatternFill("solid", fgColor="1E3A5F")
    section_fill = PatternFill("solid", fgColor="2E5984")
    sub_fill = PatternFill("solid", fgColor="EBF2FA")
    result_fill = PatternFill("solid", fgColor="E8F5E9")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    section_font = Font(color="FFFFFF", bold=True, size=10)
    bold = Font(bold=True)
    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center")
    wrap = Alignment(wrap_text=True, vertical="top")

    def hdr(ws, row, col, val, fill=header_fill, font=header_font):
        cell = ws.cell(row=row, column=col, value=val)
        cell.fill = fill
        cell.font = font
        cell.alignment = center
        cell.border = border
        return cell

    def cell(ws, row, col, val, bold_=False, fill_=None, align=None):
        c = ws.cell(row=row, column=col, value=val)
        if bold_: c.font = bold
        if fill_: c.fill = fill_
        if align: c.alignment = align
        c.border = border
        return c

    # ══════════════════════════════════════════════
    # Sheet 1: Job Info
    # ══════════════════════════════════════════════
    ws1 = wb.active
    ws1.title = "Job Info"
    ws1.column_dimensions["A"].width = 30
    ws1.column_dimensions["B"].width = 40

    hdr(ws1, 1, 1, "JOB ARCHITECTURE EVALUATION", header_fill, header_font)
    ws1.merge_cells("A1:B1")

    fields = [
        ("Candidate / Role Name", s.get("job_name", "")),
        ("Job Title", s.get("job_title", "")),
        ("Evaluator", s.get("evaluator", "")),
        ("Evaluation Date", s.get("eval_date", "")),
        ("Department / Team", s.get("department", "")),
        ("Notes", s.get("job_notes", "")),
    ]
    for i, (label, value) in enumerate(fields, start=2):
        cell(ws1, i, 1, label, bold_=True)
        c = ws1.cell(row=i, column=2, value=value)
        c.border = border
        c.alignment = wrap

    # ══════════════════════════════════════════════
    # Sheet 2: Scoring Details
    # ══════════════════════════════════════════════
    ws2 = wb.create_sheet("Scoring Details")
    ws2.column_dimensions["A"].width = 35
    ws2.column_dimensions["B"].width = 12
    ws2.column_dimensions["C"].width = 12
    ws2.column_dimensions["D"].width = 12
    ws2.column_dimensions["E"].width = 45

    hdr(ws2, 1, 1, "Dimension / Sub-dimension", header_fill, header_font)
    hdr(ws2, 1, 2, "Score (0-5)", header_fill, header_font)
    hdr(ws2, 1, 3, "Weight", header_fill, header_font)
    hdr(ws2, 1, 4, "Dim. Score", header_fill, header_font)
    hdr(ws2, 1, 5, "Comments", header_fill, header_font)

    def add_section(row, name, dim_score, weight, comment=""):
        c = ws2.cell(row=row, column=1, value=name)
        c.fill = section_fill; c.font = section_font; c.border = border; c.alignment = wrap
        ws2.cell(row=row, column=2, value="").border = border
        ws2.cell(row=row, column=3, value=weight).border = border
        ws2.cell(row=row, column=3).alignment = center
        ws2.cell(row=row, column=4, value=round(dim_score, 3)).border = border
        ws2.cell(row=row, column=4).alignment = center
        c2 = ws2.cell(row=row, column=5, value=comment)
        c2.border = border; c2.alignment = wrap
        return row + 1

    def add_sub(row, name, score, weight=""):
        c = ws2.cell(row=row, column=1, value=f"  {name}")
        c.fill = sub_fill; c.border = border; c.alignment = wrap
        ws2.cell(row=row, column=2, value=score).border = border
        ws2.cell(row=row, column=2).alignment = center
        ws2.cell(row=row, column=3, value=weight).border = border
        ws2.cell(row=row, column=3).alignment = center
        ws2.cell(row=row, column=4, value="").border = border
        ws2.cell(row=row, column=5, value="").border = border
        return row + 1

    row = 2

    # Technical Competency
    row = add_section(row, "1. Technical Competency", scores["tc_score"], "12.5%",
                      s.get("comment_tc", ""))
    row = add_sub(row, "Legal / Core competency", s.get("tc_legal", 2), "20%")
    row = add_sub(row, "Data", s.get("tc_data", 2), "20%")
    row = add_sub(row, "Strategy", s.get("tc_strategy", 2), "20%")
    row = add_sub(row, "Leadership", s.get("tc_leadership", 2), "20%")
    row = add_sub(row, "Transformational", s.get("tc_transformational", 2), "20%")

    # Behavioural Competency
    row = add_section(row, "2. Behavioural Competency", scores["bc_score"], "12.5%",
                      s.get("comment_bc", ""))
    row = add_sub(row, "IC – Client problem complexity", s.get("bc_ic_client_problem", 2))
    row = add_sub(row, "IC – Client system complexity", s.get("bc_ic_client_system", 2))
    row = add_sub(row, "IC – Team interaction", s.get("bc_ic_team", 2))
    row = add_sub(row, "IC – Organizational interaction", s.get("bc_ic_org", 2))
    row = add_sub(row, f"Interaction Complexity (computed: {scores['bc_ic']})", scores["bc_ic"], "30%")
    row = add_sub(row, "Frequency", s.get("bc_frequency", 2), "25%")
    row = add_sub(row, "Consequence", s.get("bc_consequence", 2), "25%")
    row = add_sub(row, "Conflict", s.get("bc_conflict", 2), "20%")

    # Effort
    row = add_section(row, "3. Effort", scores["effort_score"], "12.5%",
                      s.get("comment_ef", ""))
    row = add_sub(row, "Mental: Concentration & focus", s.get("ef_concentration", 2))
    row = add_sub(row, "Mental: Problem-solving complexity", s.get("ef_complexity", 2))
    row = add_sub(row, "Mental: Information processing", s.get("ef_information", 2))
    row = add_sub(row, "Mental: Multitasking demands", s.get("ef_multitasking", 2))
    row = add_sub(row, "Mental: Switching roles", s.get("ef_switching", 2))
    row = add_sub(row, "Emotional: Regulating own emotions", s.get("ef_own_emotions", 2))
    row = add_sub(row, "Emotional: Managing others' emotions", s.get("ef_others_emotions", 2))
    row = add_sub(row, "Emotional: Conflict & distress", s.get("ef_conflict", 2))
    row = add_sub(row, "Emotional: Professional demeanor", s.get("ef_pressure", 2))

    # Professional Capital
    row = add_section(row, "4. Professional Capital", scores["pc_score"], "25%",
                      s.get("comment_pc", ""))
    row = add_sub(row, "Professional credibility", s.get("pc_credibility", 2), "1/3")
    row = add_sub(row, "Relational capital", s.get("pc_relational", 2), "1/3")
    row = add_sub(row, "Organizational capital", s.get("pc_organizational", 2), "1/3")

    # Working Conditions
    row = add_section(row, "5. Working Conditions", scores["wc_score"], "12.5%",
                      s.get("comment_wc", ""))
    row = add_sub(row, "Schedule demands", s.get("wc_schedule", 2), "33%")
    row = add_sub(row, "Travel demands", s.get("wc_travel", 2), "33%")
    row = add_sub(row, "Social & organizational environment", s.get("wc_social", 2), "33%")

    # Level of Responsibility
    row = add_section(row, "6. Level of Responsibility", scores["resp_score"], "25%",
                      s.get("comment_resp", ""))
    row = add_sub(row, "Scope of impact", s.get("resp_scope", 2), "25%")
    row = add_sub(row, "Autonomy & decision-making authority", s.get("resp_autonomy", 2), "25%")
    row = add_sub(row, "Reversibility & risk", s.get("resp_reversibility", 2), "25%")
    row = add_sub(row, "Decision complexity & frequency", s.get("resp_decision", 2), "25%")

    # ══════════════════════════════════════════════
    # Sheet 3: Results & Pay Proposal
    # ══════════════════════════════════════════════
    ws3 = wb.create_sheet("Results & Pay Proposal")
    ws3.column_dimensions["A"].width = 35
    ws3.column_dimensions["B"].width = 20
    ws3.column_dimensions["C"].width = 20

    hdr(ws3, 1, 1, "RESULTS & PAY PROPOSAL", header_fill, header_font)
    ws3.merge_cells("A1:C1")

    # Score summary
    r = 2
    hdr(ws3, r, 1, "Dimension", section_fill, section_font)
    hdr(ws3, r, 2, "Score (0–5)", section_fill, section_font)
    hdr(ws3, r, 3, "Weight", section_fill, section_font)
    r += 1

    summary_rows = [
        ("Technical Competency", scores["tc_score"], "12.5%"),
        ("Behavioural Competency", scores["bc_score"], "12.5%"),
        ("Effort", scores["effort_score"], "12.5%"),
        ("Professional Capital", scores["pc_score"], "25%"),
        ("Working Conditions", scores["wc_score"], "12.5%"),
        ("Level of Responsibility", scores["resp_score"], "25%"),
    ]
    for dim, sc, wt in summary_rows:
        cell(ws3, r, 1, dim)
        c2 = ws3.cell(row=r, column=2, value=round(sc, 3)); c2.border = border; c2.alignment = center
        c3 = ws3.cell(row=r, column=3, value=wt); c3.border = border; c3.alignment = center
        r += 1

    # Final score
    ws3.cell(row=r, column=1, value="FINAL SCORE (raw)").border = border
    ws3.cell(row=r, column=1).font = bold
    c2 = ws3.cell(row=r, column=2, value=round(scores["final"], 3)); c2.border = border; c2.alignment = center
    ws3.cell(row=r, column=3, value="").border = border
    r += 1

    ws3.cell(row=r, column=1, value="FINAL SCORE (rounded down)").border = border
    ws3.cell(row=r, column=1).font = Font(bold=True, size=12)
    c2 = ws3.cell(row=r, column=2, value=scores["final_rounded"])
    c2.border = border; c2.alignment = center; c2.font = Font(bold=True, size=12)
    ws3.cell(row=r, column=3, value="").border = border
    r += 2

    # Pay level
    cat = lookup_pay_level(scores["final_rounded"])
    pay = PAY_STRUCTURE.get(cat, {})

    hdr(ws3, r, 1, "PAY PROPOSAL", section_fill, section_font)
    ws3.merge_cells(f"A{r}:C{r}")
    r += 1

    pay_rows = [
        ("Pay Level / Category", cat),
        ("Base Monthly Salary (gross)", f"€ {pay.get('salary', 0):,.2f}"),
        ("Annual Salary (× 13.92)", f"€ {pay.get('salary', 0) * 13.92:,.2f}"),
        ("Mobility Budget / Company Car", f"€ {pay.get('mobility', 0):,.0f} / month"),
        ("Home Work Allowance", f"€ {pay.get('home_allowance', 0):,.0f} / month"),
        ("Meal Vouchers", "€ 10 / worked day (employer: €8.91)"),
        ("Ecovouchers", "€ 250 / year"),
        ("Yearly Premium (2026)", "€ 330.84"),
        ("Supplementary Pension", "% of 12 × monthly base salary"),
        ("Collective Bonus Eligibility", "Up to €3,700 net / year (FTE)"),
        ("Paid Days Off", "45 days / year (FTE)"),
        ("Overall Comments", s.get("overall_comments", "")),
    ]
    for label, value in pay_rows:
        c1 = ws3.cell(row=r, column=1, value=label); c1.border = border; c1.font = bold
        c2 = ws3.cell(row=r, column=2, value=value); c2.border = border; c2.alignment = wrap
        ws3.merge_cells(f"B{r}:C{r}")
        r += 1

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

# ──────────────────────────────────────────────────────────────────────────────
# PAGE COMPONENTS
# ──────────────────────────────────────────────────────────────────────────────
def score_slider(label, key, default=2, help_text=None):
    val = st.select_slider(
        label,
        options=list(range(6)),
        value=st.session_state.get(key, default),
        format_func=lambda x: SCORE_LABELS[x],
        key=key,
        help=help_text,
    )
    return val

def comment_box(label, key):
    st.text_area(
        label,
        value=st.session_state.get(key, ""),
        key=key,
        height=100,
        placeholder="Add comments, justification, or context here…",
    )

def section_header(icon, title, subtitle=None):
    st.markdown(f"## {icon} {title}")
    if subtitle:
        st.caption(subtitle)
    st.divider()

def mini_score_card(label, score, weight):
    col1, col2, col3 = st.columns([3, 1, 1])
    col1.write(label)
    col2.metric("Score", f"{score:.2f}")
    col3.metric("Weight", weight)

# ──────────────────────────────────────────────────────────────────────────────
# PAGES
# ──────────────────────────────────────────────────────────────────────────────
def page_job_info():
    section_header("🏠", "Job Information", "Enter basic information about the role being evaluated.")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Candidate / Role Name", key="job_name",
                      value=st.session_state.get("job_name", ""))
        st.text_input("Job Title", key="job_title",
                      value=st.session_state.get("job_title", ""))
        st.text_input("Department / Team", key="department",
                      value=st.session_state.get("department", ""))
    with col2:
        st.text_input("Evaluator", key="evaluator",
                      value=st.session_state.get("evaluator", ""))
        st.date_input("Evaluation Date", key="eval_date",
                      value=st.session_state.get("eval_date", None) or "today")
        st.text_area("General Notes", key="job_notes",
                     value=st.session_state.get("job_notes", ""),
                     height=80,
                     placeholder="Any general notes about this evaluation…")

    st.divider()
    st.info("""
**About this tool**

This app implements the Stratarius job architecture scoring model. Fill in each section
using scores from **0 to 5**:
- **0** = Not present / Not applicable
- **1** = Basic / Entry level
- **2** = Developing / Moderate
- **3** = Proficient / Solid
- **4** = Advanced / Strong
- **5** = Expert / Exceptional

Navigate through the pages using the sidebar. The **Results & Pay Proposal** page will
calculate the final score and suggest the appropriate pay level.
""")


def page_technical():
    section_header("🧠", "Technical Competency",
                   "Weight: 12.5% of total score | Score is minimum 0 and 1 in at least one domain")

    st.info("""
**What we measure:** The level and breadth of technical expertise across five domains.
Within Stratarius, leadership belongs to technical capability because leadership without
expertise has no legitimacy. Expertise is the basis of authority.
""")

    st.markdown("### Sub-dimensions")
    score_slider("Legal (or other core competency, e.g. psychology)", "tc_legal",
                 help_text="Solid legal expertise, ability to apply legal reasoning to business questions")
    score_slider("Data", "tc_data",
                 help_text="Data literacy, ability to work with structured analyses and computations")
    score_slider("Strategy", "tc_strategy",
                 help_text="Strategic thinking, ability to integrate insights across domains")
    score_slider("Leadership", "tc_leadership",
                 help_text="Capability to support peers, knowledge sharing, create trust and psychological safety")
    score_slider("Transformational", "tc_transformational",
                 help_text="Interest and capability to drive change and expand expertise")

    tc = sum([
        st.session_state.get("tc_legal", 2),
        st.session_state.get("tc_data", 2),
        st.session_state.get("tc_strategy", 2),
        st.session_state.get("tc_leadership", 2),
        st.session_state.get("tc_transformational", 2),
    ]) / 5

    st.divider()
    st.metric("Technical Competency Score (average)", f"{tc:.2f} / 5")

    st.divider()
    comment_box("💬 Comments on Technical Competency", "comment_tc")


def page_behavioural():
    section_header("👥", "Behavioural Competency",
                   "Weight: 12.5% of total score | Geometric weighted mean")

    st.info("""
**What we measure:** How the person interacts with clients, teams, and the organisation,
and how they handle conflict and complexity. The overall score is a **weighted geometric mean**,
meaning a very low score on any one dimension significantly pulls down the total.
""")

    st.markdown("### Interaction Complexity sub-scores")
    st.caption("Rule: if ≥2 sub-scores = 5 → IC = 5 | if ≥2 sub-scores = 4 → IC = 4 | otherwise: rounded average")

    score_slider("Complexity / ambiguity of the client problem", "bc_ic_client_problem",
                 help_text="How complex or ambiguous is the client's core problem?")
    score_slider("Complexity / ambiguity of the client system", "bc_ic_client_system",
                 help_text="How complex is the client stakeholder system (number of stakeholders, politics, etc.)?")
    score_slider("Team interaction", "bc_ic_team",
                 help_text="How complex is the required team interaction and collaboration?")
    score_slider("Organizational interaction", "bc_ic_org",
                 help_text="How complex is the interaction with the broader organization?")

    ic_subs = [
        st.session_state.get("bc_ic_client_problem", 2),
        st.session_state.get("bc_ic_client_system", 2),
        st.session_state.get("bc_ic_team", 2),
        st.session_state.get("bc_ic_org", 2),
    ]
    ic = calculate_interaction_complexity(ic_subs)
    st.metric("→ Interaction Complexity (computed)", f"{ic} / 5")

    st.divider()
    st.markdown("### Other behavioural dimensions")
    score_slider("Frequency of interaction", "bc_frequency",
                 help_text="How frequently does the role require complex interactions? (weight 25%)")
    score_slider("Consequence of interaction", "bc_consequence",
                 help_text="How significant are the consequences of interaction quality? (weight 25%)")
    score_slider("Conflict handling", "bc_conflict",
                 help_text="How much conflict, resistance, or competing expectations must be managed? (weight 20%)")

    # Compute BC
    ic_n = ic / 5
    freq_n = st.session_state.get("bc_frequency", 2) / 5
    cons_n = st.session_state.get("bc_consequence", 2) / 5
    conf_n = st.session_state.get("bc_conflict", 2) / 5
    if all(v > 0 for v in [ic_n, freq_n, cons_n, conf_n]):
        bc = round((ic_n**0.3 * freq_n**0.25 * cons_n**0.25 * conf_n**0.2) * 5, 2)
    else:
        bc = 0.0

    st.divider()
    st.metric("Behavioural Competency Score (geometric mean)", f"{bc:.2f} / 5")

    st.divider()
    comment_box("💬 Comments on Behavioural Competency", "comment_bc")


def page_effort():
    section_header("💪", "Effort",
                   "Weight: 12.5% of total score | Mental effort 50% + Emotional effort 50%")

    st.info("""
**What we measure:** The cognitive and emotional demands placed on the role.
Mental and emotional effort each contribute equally (50%) to the Effort dimension.
""")

    st.markdown("### Mental Effort")
    score_slider("Concentration and focus required", "ef_concentration",
                 help_text="Level of sustained attention and focus the role requires (weight 15%)")
    score_slider("Complexity of problem-solving", "ef_complexity",
                 help_text="How complex are the problems that need to be solved? (weight 25%)")
    score_slider("Amount of information to process and retain", "ef_information",
                 help_text="Volume and complexity of information to process (weight 25%)")
    score_slider("Multitasking demands", "ef_multitasking",
                 help_text="How much simultaneous task management is required? (weight 15%)")
    score_slider("Switching roles", "ef_switching",
                 help_text="How often must the person switch between different modes or roles? (weight 20%)")

    mental_subs = [
        st.session_state.get("ef_concentration", 2),
        st.session_state.get("ef_complexity", 2),
        st.session_state.get("ef_information", 2),
        st.session_state.get("ef_multitasking", 2),
        st.session_state.get("ef_switching", 2),
    ]
    mental = (sum(mental_subs) / len(mental_subs)) * 0.5
    st.metric("→ Mental Effort contribution", f"{mental:.2f}")

    st.divider()
    st.markdown("### Emotional Effort")
    score_slider("Regulation of one's own emotions", "ef_own_emotions",
                 help_text="Degree to which the role requires managing personal emotional reactions")
    score_slider("Managing others' emotions", "ef_others_emotions",
                 help_text="Degree to which the role requires managing the emotions of others")
    score_slider("Dealing with conflict, complaints, distress", "ef_conflict",
                 help_text="Frequency and intensity of conflict or distress situations")
    score_slider("Maintaining professional demeanor under pressure", "ef_pressure",
                 help_text="Degree to which the role demands composure in high-pressure situations")

    emotional_subs = [
        st.session_state.get("ef_own_emotions", 2),
        st.session_state.get("ef_others_emotions", 2),
        st.session_state.get("ef_conflict", 2),
        st.session_state.get("ef_pressure", 2),
    ]
    emotional = (sum(emotional_subs) / len(emotional_subs)) * 0.5
    st.metric("→ Emotional Effort contribution", f"{emotional:.2f}")

    effort = mental + emotional
    st.divider()
    st.metric("Effort Score (mental + emotional)", f"{effort:.2f} / 5")

    st.divider()
    comment_box("💬 Comments on Effort", "comment_ef")


def page_professional():
    section_header("🏆", "Professional Capital",
                   "Weight: 25% of total score | Equal weight across 3 dimensions")

    st.info("""
**What we measure:** The trust, credibility, and capital the person has built.
Professional capital is one of the most heavily weighted dimensions (25%) because
Stratarius is a customer-intimate consultancy where **trust and credibility are core**.
""")

    st.markdown("### Sub-dimensions")
    score_slider("Professional credibility",  "pc_credibility",
                 help_text="Level at which advice is accepted — from emerging credibility to authority whose advice is rarely challenged")
    score_slider("Relational capital", "pc_relational",
                 help_text="Strength and breadth of professional relationships that can be activated for Stratarius")
    score_slider("Organizational capital", "pc_organizational",
                 help_text="Degree of organizational continuity built — institutional knowledge, client dependencies, key-person value")

    pc = sum([
        st.session_state.get("pc_credibility", 2),
        st.session_state.get("pc_relational", 2),
        st.session_state.get("pc_organizational", 2),
    ]) / 3

    st.divider()
    st.metric("Professional Capital Score (average)", f"{pc:.2f} / 5")

    with st.expander("📖 Score anchors for Professional Credibility"):
        st.markdown("""
| Score | Description |
|-------|-------------|
| **1–2** | Emerging credibility – advice still requires validation/escalation |
| **3** | Solid credibility – advice is generally accepted, occasional escalation |
| **4** | Strong credibility – advice normally accepted without escalation |
| **5** | Authority – recognised expert, advice rarely challenged |
""")

    with st.expander("📖 Score anchors for Relational Capital"):
        st.markdown("""
| Score | Description |
|-------|-------------|
| **1** | No meaningful professional network to activate |
| **2** | Early-stage professional connections |
| **3** | Some potential to activate relationships within Stratarius |
| **4** | Strong network with real activation potential |
| **5** | Extensive network that actively creates value for Stratarius |
""")

    with st.expander("📖 Score anchors for Organizational Capital"):
        st.markdown("""
| Score | Description |
|-------|-------------|
| **0–1** | No organizational continuity accumulated yet |
| **2–3** | Some institutional knowledge, limited client dependency |
| **4** | High institutional knowledge, key client relationships |
| **5** | Critical organizational continuity, high key-person value |
""")

    st.divider()
    comment_box("💬 Comments on Professional Capital", "comment_pc")


def page_working():
    section_header("🌍", "Working Conditions",
                   "Weight: 12.5% of total score | Equal weight across 3 dimensions")

    st.info("""
**What we measure:** The demands and constraints of the working context.
Working conditions recognize the **context** in which the role operates.
Higher scores indicate more demanding or less favourable conditions.
""")

    st.markdown("### Sub-dimensions")
    score_slider("Schedule demands", "wc_schedule",
                 help_text="Level of schedule pressure, irregular hours, on-call requirements (weight 33%)")
    score_slider("Travel demands", "wc_travel",
                 help_text="Level of travel required — frequency, duration, and disruption (weight 33%)")
    score_slider("Social and organizational environment", "wc_social",
                 help_text="Level of organizational support vs. startup-like self-reliance (weight 33%)")

    wc = sum([
        st.session_state.get("wc_schedule", 2),
        st.session_state.get("wc_travel", 2),
        st.session_state.get("wc_social", 2),
    ]) / 3

    st.divider()
    st.metric("Working Conditions Score (average)", f"{wc:.2f} / 5")

    st.divider()
    comment_box("💬 Comments on Working Conditions", "comment_wc")


def page_responsibility():
    section_header("⚖️", "Level of Responsibility",
                   "Weight: 25% of total score | Equal weight across 4 dimensions")

    st.info("""
**What we measure:** The scope, autonomy, and accountability of the role.
Responsibility is one of the most heavily weighted dimensions (25%) because
Stratarius values **accountability** and the ability to own outcomes.
""")

    st.markdown("### Sub-dimensions")
    score_slider("Scope of impact", "resp_scope",
                 help_text="Breadth of impact — from individual tasks to organizational / client-wide impact (weight 25%)")
    score_slider("Autonomy and decision-making authority", "resp_autonomy",
                 help_text="Degree of independent judgment — from guided execution to full strategic autonomy (weight 25%)")
    score_slider("Reversibility and risk", "resp_reversibility",
                 help_text="Degree to which decisions are hard to reverse or carry significant risk (weight 25%)")
    score_slider("Decision complexity and frequency", "resp_decision",
                 help_text="How complex and how frequent are the decisions the role must make? (weight 25%)")

    resp = sum([
        st.session_state.get("resp_scope", 2),
        st.session_state.get("resp_autonomy", 2),
        st.session_state.get("resp_reversibility", 2),
        st.session_state.get("resp_decision", 2),
    ]) / 4

    st.divider()
    st.metric("Level of Responsibility Score (average)", f"{resp:.2f} / 5")

    with st.expander("📖 Score anchors for Responsibility"):
        st.markdown("""
| Score | Description |
|-------|-------------|
| **1** | Accountable for own tasks only, guided execution, escalates regularly |
| **2** | Accountable for own analyses/deliverables, exercises judgment within defined boundaries |
| **3** | Accountable for project outcomes, takes autonomous decisions on client work |
| **4** | Has client-level and organizational impact, owns project outcomes |
| **5** | Full strategic ownership, shapes direction, decisions rarely reversed |
""")

    st.divider()
    comment_box("💬 Comments on Level of Responsibility", "comment_resp")


def page_results():
    section_header("📊", "Results & Pay Proposal",
                   "Summary of all scores and the resulting pay level recommendation")

    scores = calculate_scores()
    cat = lookup_pay_level(scores["final_rounded"])
    pay = PAY_STRUCTURE.get(cat, {})

    # ── Score Summary ──
    st.markdown("### Score Summary")
    cols = st.columns(3)
    summary = [
        ("🧠 Technical Competency", scores["tc_score"], "12.5%"),
        ("👥 Behavioural Competency", scores["bc_score"], "12.5%"),
        ("💪 Effort", scores["effort_score"], "12.5%"),
        ("🏆 Professional Capital", scores["pc_score"], "25%"),
        ("🌍 Working Conditions", scores["wc_score"], "12.5%"),
        ("⚖️ Responsibility", scores["resp_score"], "25%"),
    ]
    for i, (name, sc, wt) in enumerate(summary):
        with cols[i % 3]:
            st.metric(name, f"{sc:.2f} / 5", delta=f"Weight: {wt}")

    st.divider()

    # ── Final Score ──
    col1, col2, col3 = st.columns(3)
    col1.metric("Raw Final Score", f"{scores['final']:.3f}")
    col2.metric("Final Score (rounded down)", f"{scores['final_rounded']:.1f}")
    col3.metric("Pay Level", cat, delta="Recommended")

    # ── Weighted calculation detail ──
    with st.expander("🔢 Detailed calculation"):
        data = {
            "Dimension": [n for n, _, _ in summary],
            "Score": [round(sc, 3) for _, sc, _ in summary],
            "Weight": [0.125, 0.125, 0.125, 0.25, 0.125, 0.25],
            "Weighted Score": [
                round(sc * w, 4)
                for (_, sc, _), w in zip(summary, [0.125, 0.125, 0.125, 0.25, 0.125, 0.25])
            ],
        }
        df = pd.DataFrame(data)
        df.loc[len(df)] = ["**TOTAL**", "", sum(data["Weight"]), round(scores["final"], 4)]
        st.dataframe(df, hide_index=True, use_container_width=True)

    st.divider()

    # ── Pay Proposal ──
    st.markdown("### 💰 Pay Proposal")

    if pay:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
**Pay Level:** `{cat}`
**Score:** `{pay['score']}`

| Component | Amount |
|-----------|--------|
| Base monthly salary (gross) | **€ {pay['salary']:,.2f}** |
| Annual salary (× 13.92) | **€ {pay['salary'] * 13.92:,.2f}** |
| Mobility budget / company car | **€ {pay['mobility']:,} / month** |
| Home work allowance | **€ {pay['home_allowance']:,} / month** |
""")
        with col2:
            st.markdown("""
**Additional benefits (all levels):**
- Meal vouchers: €10 / worked day (employer €8.91)
- Ecovouchers: €250 / year
- Yearly premium: €330.84 (2026)
- Supplementary pension: % of 12 × monthly base
- Guaranteed income up to 100% in case of illness/accident
- Hospitalisation insurance
- Collective bonus: up to €3,700 net/year (FTE)
- 45 paid days off/year (FTE)
""")

    st.divider()

    # ── Pay Level Comparison ──
    with st.expander("📋 Full pay structure overview"):
        ps_data = []
        for cat_name, data in PAY_STRUCTURE.items():
            ps_data.append({
                "Level": cat_name,
                "Score": data["score"],
                "Base Salary (gross)": f"€ {data['salary']:,.2f}",
                "Annual (×13.92)": f"€ {data['salary'] * 13.92:,.2f}",
                "Mobility": f"€ {data['mobility']:,}",
                "Home Allowance": f"€ {data['home_allowance']:,}",
                "→ This role": "✅" if cat_name == cat else "",
            })
        st.dataframe(pd.DataFrame(ps_data), hide_index=True, use_container_width=True)

    st.divider()

    # ── Overall Comments ──
    st.markdown("### 💬 Overall Comments")
    st.text_area(
        "Overall evaluation comments",
        key="overall_comments",
        value=st.session_state.get("overall_comments", ""),
        height=120,
        placeholder="Add any overall observations, context, or rationale for the proposed pay level…",
    )

    st.divider()

    # ── Export ──
    st.markdown("### 📥 Export")
    if st.button("Generate Excel Report", type="primary", use_container_width=True):
        buf = export_to_excel(scores)
        candidate = st.session_state.get("job_name", "evaluation").replace(" ", "_")
        st.download_button(
            label="⬇️ Download Excel Report",
            data=buf,
            file_name=f"job_architecture_{candidate}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


def page_reward_strategy():
    section_header("ℹ️", "Reward Strategy",
                   "Background information from the Stratarius Reward Strategy document")

    tab1, tab2, tab3, tab4 = st.tabs(["📌 Philosophy", "📐 Scoring Logic", "💼 Profile Examples", "🎁 Total Package"])

    with tab1:
        st.markdown("""
### Reward Philosophy

> *"At Stratarius we primarily value (and therefore reward) technical and behavioural competence,
> professional credibility and responsibility, while recognizing effort and working conditions as
> important but secondary job factors."*

| Category | Message |
|----------|---------|
| **Competency** | We value capability — technical (multidisciplinary) and behavioural capabilities are equally important |
| **Professional Capital** | We value trust and credibility |
| **Responsibility** | We value accountability |
| **Effort** | We recognize burden |
| **Working Conditions** | We recognize context |

### Pay Levels

The job architecture consists of approximately **41 pay levels** across 5 categories:
- **A**: A5 to A9 (anything below A5 is theoretical)
- **B**: B0 to B9
- **C**: C0 to C9
- **D**: D0 to D9
- **E**: E0 to E5 (anything above E5 is theoretical)

### Governance

The pay level is determined based on:
1. **Capabilities of the individual** (looking back — what they can bring to the table)
2. **Job demands** (looking forward — what they should bring to the table)

The assessment is done by both Stratarius and the individual. This process is **completely transparent**
and is the subject of an open discussion. The pay level is the outcome of a **principled negotiation**
and is therefore non-negotiable. However, the principles and how to apply them are subject to dialogue.

### Pay Progression

- At least once a year during Q1, an assessment is done regarding the adequacy of the pay level
- At any given time, both the individual and Stratarius can take initiative to evaluate
""")

    with tab2:
        st.markdown("""
### Dimension Weights

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Technical Competency | 12.5% | Core capability |
| Behavioural Competency | 12.5% | Core capability (equal to technical) |
| Professional Capital | **25%** | Trust and credibility — most critical |
| Level of Responsibility | **25%** | Accountability — most critical |
| Effort | 12.5% | Recognized but secondary |
| Working Conditions | 12.5% | Context — recognized but secondary |

### How Scores Work

**Technical Competency:** Simple arithmetic average of 5 sub-dimensions.
*Note: minimum score of 0 or 1 is required in at least one domain.*

**Behavioural Competency:** Weighted **geometric mean** — a very low score on any single dimension
significantly reduces the overall BC score. This captures that behavioural capabilities need to be
sufficiently developed across all dimensions.

- Interaction Complexity (30%)
- Frequency (25%)
- Consequence (25%)
- Conflict (20%)

**Interaction Complexity special rule:**
- If ≥2 sub-scores = 5 → IC = 5 (regardless of average)
- If ≥2 sub-scores = 4 → IC = 4 (regardless of average)
- Otherwise: rounded arithmetic average

**Effort:** Average of Mental Effort (50%) + Average of Emotional Effort (50%)

**Professional Capital, Working Conditions, Responsibility:** Simple arithmetic averages.

**Final Score:** Weighted sum of all 6 dimensions → rounded **down** to 1 decimal
""")

    with tab3:
        st.markdown("""
### Profile Example 1 — Pay Level B6

**Role:** HR legal expert with ~5 years of experience and good knowledge of Excel

**Technical Capability:**
- Solid legal expertise in employment, reward, or people governance
- Ability to apply legal reasoning to business questions
- Sufficient data literacy for structured analyses (Excel)
- Ability to integrate legal insight with strategic/quantitative considerations
- Leadership: capability to support peers, proactive knowledge sharing

**Behavioural Competency:**
- Operates in ambiguous client situations (mainly client problem, less client system)
- Professional interaction with multiple stakeholders
- Comfortable in team-based project environments
- Manages disagreement, resistance, and competing expectations

**Professional Capital:** Emerging professional credibility (advice still requires some validation)

**Responsibility:**
- Accountable for own analyses, advice, and deliverables
- Exercises judgment within defined boundaries
- Escalates appropriately; contributes without owning strategic direction

**Resulting pay (B6):** €4,489.80 gross/month
""")
        st.divider()
        st.markdown("""
### Profile Example 2 — Pay Level C4

**Role:** HR legal expert with ~10 years of experience

**Technical Capability:**
- HR legal authority — defines positions in complex, sensitive, or high-impact contexts
- Capable of shaping HR legal / reward legal frameworks
- Capable of leading teams, projects or workstreams based on subject-matter authority
- Data literate; integrates legal insight with strategic and quantitative considerations

**Behavioural Competency:**
- Operates largely autonomously in ambiguous client situations (both problem and system)
- Professional interaction with multiple stakeholders; manages disagreement

**Professional Capital:**
- Demonstrates credibility — advice normally accepted without escalation
- Has built professional relationships with some potential to activate within Stratarius

**Responsibility:**
- Has client-level and organizational impact
- Takes decisions autonomously relating to clients and projects
- Owns project outcomes

**Resulting pay (C4):** €6,633.47 gross/month
""")

    with tab4:
        st.markdown("""
### Total Compensation Package

All Stratarius employees are entitled to:

**Financial Well-being:**
| Component | Details |
|-----------|---------|
| Base monthly salary | Paid 13.92× per year |
| Company car or mobility budget | Worker's choice — A: €780 | B: €930 | C: €1,080 | D: €1,230 | E: €1,380 |
| Meal vouchers | €10/worked day (employer: €8.91, employee: €1.09) |
| Home work allowance | €150/month (if ≥1 day/week from home) |
| Ecovouchers | €250/year |
| Yearly premium | €330.84 (2026) |
| Supplementary pension | % of 12 × monthly base salary |
| Guaranteed income insurance | Up to 100% regular net income (illness/accident) |
| Hospitalisation insurance | Includes option to affiliate family members |
| Collective bonus | Up to €3,700 net/year (FTE), based on Stratarius performance |
| Share purchase option | Possibility to purchase Stratarius shares |
| Paid days off | 45 days/year FTE (10 public + 20 statutory + 15 extra-legal) |

**Professional Well-being:**
- Offices in Ghent (HQ) and Leuven
- Full office setup: MacBook Air/Dell XPS, curved screen, ergonomic peripherals, headset, reMarkable Pro
- Full remote setup: phone + data, curved screen, ergonomic peripherals, internet at home
- Large autonomy regarding where and when you work

**Eudaimonic Well-being:**
- LinkedIn Premium including LinkedIn Learning
- Networking events in Belgium and abroad
- Workation opportunities
- Formal education, knowledge bases, on-the-job training
- Public speaking / personal brand opportunities
- Room for research and experimentation
- A learning culture with peers eager to share and grow
""")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Job Architecture Scoring — Stratarius",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS
    st.markdown("""
    <style>
    .stSelectSlider > div { font-size: 13px; }
    .metric-container { background: #f8f9fa; border-radius: 8px; padding: 12px; }
    [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    with st.sidebar:
        st.markdown("## ⚖️ Job Architecture")
        st.markdown("**Stratarius Scoring Tool**")
        st.divider()

        page = st.radio(
            "Navigate",
            options=[
                "🏠 Job Information",
                "🧠 Technical Competency",
                "👥 Behavioural Competency",
                "💪 Effort",
                "🏆 Professional Capital",
                "🌍 Working Conditions",
                "⚖️ Level of Responsibility",
                "📊 Results & Pay Proposal",
                "ℹ️ Reward Strategy",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        # Mini live score preview
        scores = calculate_scores()
        st.markdown("**Live Score Preview**")
        st.markdown(f"Final score: **{scores['final_rounded']:.1f}**")
        cat = lookup_pay_level(scores["final_rounded"])
        pay = PAY_STRUCTURE.get(cat, {})
        st.markdown(f"Pay level: **{cat}**")
        st.markdown(f"Salary: **€{pay.get('salary', 0):,.0f}/mo**")
        st.progress(min(scores["final_rounded"] / 4.5, 1.0))

    # Page routing
    if page == "🏠 Job Information":
        page_job_info()
    elif page == "🧠 Technical Competency":
        page_technical()
    elif page == "👥 Behavioural Competency":
        page_behavioural()
    elif page == "💪 Effort":
        page_effort()
    elif page == "🏆 Professional Capital":
        page_professional()
    elif page == "🌍 Working Conditions":
        page_working()
    elif page == "⚖️ Level of Responsibility":
        page_responsibility()
    elif page == "📊 Results & Pay Proposal":
        page_results()
    elif page == "ℹ️ Reward Strategy":
        page_reward_strategy()


if __name__ == "__main__":
    main()
