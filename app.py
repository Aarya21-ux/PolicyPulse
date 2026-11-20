import html
import math
import threading
from datetime import date, datetime
from collections import defaultdict

import pandas as pd
import streamlit as st
import db, ingest, checks, verifier, llm, embed


# ============================================================
# POLICY PULSE — PREMIUM ENTERPRISE UI
# Existing Db2/backend modules and core workflows are retained.
# New features are implemented in this file using existing data.
# ============================================================

st.set_page_config(
    page_title="PolicyPulse | Expense Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --bg:#080d18; --panel:#101a2b; --panel2:#142139; --line:rgba(157,177,216,.14);
  --text:#edf3ff; --muted:#8b9bb8; --blue:#6d8cff; --violet:#a78bfa;
  --cyan:#48d9e8; --green:#38d9a9; --red:#fb7185; --amber:#fbbf65;
}
html, body, [class*="css"], .stApp {font-family:'DM Sans','Manrope',sans-serif;}
.stApp {
 background:
 radial-gradient(900px 520px at 5% -5%,rgba(67,100,255,.19),transparent 65%),
 radial-gradient(850px 520px at 100% 0%,rgba(143,91,255,.16),transparent 60%),
 radial-gradient(700px 450px at 55% 100%,rgba(39,190,211,.07),transparent 65%),
 var(--bg);
 color:var(--text);
}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],footer,#MainMenu {background:transparent;display:none;}
.block-container {max-width:1500px;padding-top:1.5rem;padding-bottom:3.5rem;}
h1,h2,h3,h4,p,label {font-family:'DM Sans',sans-serif;}
h1,h2,h3,h4 {color:#f2f6ff;}
p {color:#b4c0d6;}
small {color:var(--muted);}

/* App header */
.pp-header {
 display:flex;justify-content:space-between;align-items:center;gap:18px;
 padding:19px 23px;margin-bottom:22px;border:1px solid var(--line);
 border-radius:20px;background:linear-gradient(120deg,rgba(20,32,56,.94),rgba(15,23,40,.86));
 box-shadow:0 15px 45px rgba(0,0,0,.20);backdrop-filter:blur(18px);
 animation:enter .55s ease both;
}
.pp-brand {display:flex;align-items:center;gap:14px;}
.pp-logo {
 width:48px;height:48px;display:grid;place-items:center;border-radius:15px;
 color:white;font-size:23px;background:linear-gradient(135deg,#527bff,#9b63ef);
 box-shadow:0 8px 25px rgba(99,102,241,.34);
}
.pp-name {font-size:1.35rem;font-weight:800;letter-spacing:-.6px;color:#fff;line-height:1.1;}
.pp-sub {font-size:.75rem;color:#91a2c2;margin-top:5px;}
.pp-status {display:flex;gap:9px;flex-wrap:wrap;justify-content:flex-end;}
.pp-pill {display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);
 background:rgba(255,255,255,.045);padding:8px 12px;border-radius:30px;
 font-size:.72rem;font-weight:700;color:#c8d4e9;}
.pp-dot {width:7px;height:7px;border-radius:50%;background:#38d9a9;box-shadow:0 0 10px #38d9a9;}

/* Page intro */
.page-kicker {font-size:.69rem;text-transform:uppercase;letter-spacing:1.6px;color:#8da6ff;font-weight:800;margin-bottom:7px;}
.page-title {font-size:1.75rem;line-height:1.15;font-weight:800;letter-spacing:-.8px;color:#f5f7ff;margin:0;}
.page-desc {font-size:.84rem;color:#8fa0bd;margin-top:7px;margin-bottom:18px;}

/* Navigation */
.stTabs [data-baseweb="tab-list"] {
 gap:6px;padding:7px;background:rgba(15,25,43,.88);border:1px solid var(--line);
 border-radius:15px;width:100%;overflow-x:auto;margin:0 0 20px;
}
.stTabs [data-baseweb="tab"] {height:42px;padding:0 17px;border-radius:10px;background:transparent;}
.stTabs [data-baseweb="tab"] p {font-size:.79rem;font-weight:700;color:#91a1bd;}
.stTabs [aria-selected="true"] {background:linear-gradient(115deg,#5278ff,#8359e9)!important;box-shadow:0 5px 18px rgba(91,111,255,.25);}
.stTabs [aria-selected="true"] p {color:white!important;}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"] {display:none;}

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
 background:linear-gradient(145deg,rgba(20,32,54,.91),rgba(13,22,38,.94))!important;
 border:1px solid var(--line)!important;border-radius:17px!important;
 padding:14px 16px;box-shadow:0 10px 30px rgba(0,0,0,.14);
 transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;
 animation:enter .45s ease both;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
 border-color:rgba(111,143,255,.36)!important;box-shadow:0 14px 36px rgba(0,0,0,.2);
}
@keyframes enter {from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer {0%{background-position:0% 50%}100%{background-position:100% 50%}}
.pp-section {display:flex;align-items:center;justify-content:space-between;gap:10px;margin:3px 0 14px;}
.pp-section-title {font-size:1rem;font-weight:800;color:#f0f4ff;}
.pp-section-sub {font-size:.7rem;color:#8092b2;text-align:right;}
.pp-divider {height:1px;background:var(--line);margin:12px 0;}

/* KPI */
.pp-kpi {position:relative;overflow:hidden;padding:17px 18px;border-radius:16px;
 background:linear-gradient(145deg,rgba(24,39,66,.96),rgba(15,25,43,.96));
 border:1px solid var(--line);min-height:126px;transition:.25s ease;}
.pp-kpi:hover {transform:translateY(-4px);border-color:rgba(109,140,255,.5);box-shadow:0 12px 30px rgba(0,0,0,.2);}
.pp-kpi:after {content:"";position:absolute;width:120px;height:120px;right:-45px;top:-55px;border-radius:50%;
 background:radial-gradient(circle,rgba(105,130,255,.20),transparent 70%);}
.pp-kpi-label {font-size:.68rem;letter-spacing:.8px;text-transform:uppercase;font-weight:800;color:#91a2c0;}
.pp-kpi-value {font-size:1.85rem;font-weight:800;letter-spacing:-1px;color:#f7f9ff;margin-top:9px;}
.pp-kpi-note {font-size:.7rem;color:#7f91b0;margin-top:4px;}
.pp-kpi-icon {float:right;font-size:1.15rem;opacity:.85;}
.pp-hero {position:relative;overflow:hidden;padding:23px 25px;border-radius:19px;
 background:linear-gradient(115deg,#6e91ff,#9583f2 55%,#60c9dd);background-size:180% 180%;
 animation:shimmer 10s ease infinite alternate;min-height:220px;box-shadow:0 16px 38px rgba(94,112,255,.18);}
.pp-hero:after {content:"";position:absolute;width:230px;height:230px;border:1px solid rgba(255,255,255,.25);
 border-radius:50%;right:-65px;top:-105px;box-shadow:0 0 0 25px rgba(255,255,255,.055),0 0 0 55px rgba(255,255,255,.035);}
.pp-hero-label {font-size:.8rem;color:#263e68;font-weight:800;}
.pp-hero-value {font-size:3.5rem;line-height:1.05;font-weight:900;letter-spacing:-2px;color:#101d3a;margin-top:12px;}
.pp-hero-value span {font-size:1.4rem;}
.pp-hero-note {font-size:.75rem;color:#2c4774;margin-top:7px;font-weight:600;}
.pp-hero-track {height:9px;border-radius:20px;background:rgba(16,29,58,.17);margin-top:17px;overflow:hidden;}
.pp-hero-track span {display:block;height:100%;background:#172d68;border-radius:20px;}

/* Status and data rows */
.pp-row {display:flex;align-items:center;gap:11px;padding:11px 5px;border-bottom:1px solid rgba(150,170,210,.09);}
.pp-row:last-child {border-bottom:0;}
.pp-avatar {width:36px;height:36px;border-radius:11px;display:grid;place-items:center;
 background:linear-gradient(135deg,#5b7dff,#9760ed);font-weight:800;color:white;flex:none;}
.pp-row-main {min-width:0;flex:1;}
.pp-row-name {font-size:.82rem;font-weight:800;color:#eff4ff;}
.pp-row-meta {font-size:.68rem;color:#8495b3;margin-top:3px;}
.pp-row-right {text-align:right;font-size:.8rem;font-weight:800;color:#fb8297;}
.pp-tag {display:inline-block;padding:4px 9px;border-radius:30px;font-size:.65rem;font-weight:800;
 background:rgba(108,135,255,.15);color:#a9bcff;}
.pp-tag.green {background:rgba(56,217,169,.13);color:#50dfb0;}
.pp-tag.red {background:rgba(251,113,133,.13);color:#fb8297;}
.pp-tag.amber {background:rgba(251,191,101,.13);color:#fbc77b;}
.pp-risk {display:flex;align-items:center;gap:10px;margin:9px 0;}
.pp-risk-track {height:7px;flex:1;border-radius:20px;background:rgba(255,255,255,.08);overflow:hidden;}
.pp-risk-track span {display:block;height:100%;border-radius:20px;}
.pp-muted {font-size:.73rem;color:#8798b5;}
.pp-callout {padding:13px 15px;border:1px solid rgba(112,143,255,.22);background:rgba(91,117,255,.07);
 border-radius:13px;color:#c8d5f0;font-size:.78rem;line-height:1.55;}
.pp-clause {padding:14px 16px;border-radius:13px;background:rgba(99,119,255,.055);
 border:1px solid var(--line);margin-bottom:10px;color:#d8e2f5;font-size:.84rem;line-height:1.7;}
.pp-claim {padding:13px 15px;border:1px solid var(--line);border-radius:13px;background:rgba(255,255,255,.025);margin-bottom:9px;}
.pp-claim-head {display:flex;justify-content:space-between;align-items:center;gap:10px;}
.pp-claim-name {font-size:.83rem;font-weight:800;color:#f1f5ff;text-transform:capitalize;}
.pp-claim-values {font-size:.75rem;color:#9babc5;margin-top:8px;}

/* Inputs */
.stTextInput input,.stNumberInput input,.stTextArea textarea,
div[data-baseweb="select"]>div {
 background:#0d1728!important;border:1px solid rgba(145,166,207,.20)!important;
 border-radius:10px!important;color:#f1f5ff!important;
}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus {
 border-color:#7892ff!important;box-shadow:0 0 0 3px rgba(105,130,255,.13)!important;
}
label,.stSelectbox label,.stTextInput label,.stNumberInput label,.stCheckbox label,.stSlider label {
 color:#c0cce2!important;font-weight:600!important;font-size:.8rem!important;
}
.stButton>button,.stDownloadButton>button {
 border-radius:10px;border:1px solid rgba(145,166,207,.2);background:rgba(255,255,255,.045);
 color:#eaf0ff;font-weight:700;min-height:40px;transition:.2s;padding:.48rem 1rem;
}
.stButton>button:hover,.stDownloadButton>button:hover {
 transform:translateY(-2px);border-color:#8298ff;background:rgba(102,127,255,.13);color:white;
}
.stButton>button[kind="primary"] {background:linear-gradient(115deg,#557cff,#8759ed);border:0;color:white;box-shadow:0 6px 18px rgba(96,112,255,.25);}
.stButton>button[kind="primary"]:hover {box-shadow:0 9px 25px rgba(96,112,255,.38);}
[data-testid="stFileUploader"] section {background:#0d1728;border:1px dashed rgba(120,145,255,.4);border-radius:13px;}
[data-testid="stDataFrame"] {border:1px solid var(--line);border-radius:12px;overflow:hidden;}
[data-testid="stExpander"] {border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.02);}
[data-testid="stMetric"] {background:rgba(255,255,255,.035);border:1px solid var(--line);border-radius:12px;padding:10px;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0e1728,#090f1c);border-right:1px solid var(--line);}
[data-testid="stSidebar"] p {color:#9aabc7;line-height:1.65;}
[data-testid="stAlert"] {border-radius:12px;}
hr {border-color:var(--line)!important;}
::-webkit-scrollbar {width:7px;height:7px;}
::-webkit-scrollbar-thumb {background:#344665;border-radius:20px;}
@media(max-width:800px) {
 .block-container{padding:1rem;}
 .pp-header{align-items:flex-start;flex-direction:column;}
 .pp-status{justify-content:flex-start;}
 .pp-hero-value{font-size:2.8rem;}
 .stTabs [data-baseweb="tab"]{padding:0 10px;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# -------------------- Shared helpers --------------------

@st.cache_resource
def _warm():
    threading.Thread(target=lambda: embed.vec("warm up"), daemon=True).start()
    return True

_warm()


def money(value):
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def section(title, subtitle=""):
    st.markdown(
        f'<div class="pp-section"><div class="pp-section-title">{html.escape(title)}</div>'
        f'<div class="pp-section-sub">{html.escape(subtitle)}</div></div>',
        unsafe_allow_html=True,
    )


def kpi(label, value, note="", icon="✦", tone=""):
    st.markdown(
        f'<div class="pp-kpi"><span class="pp-kpi-icon">{icon}</span>'
        f'<div class="pp-kpi-label">{html.escape(label)}</div>'
        f'<div class="pp-kpi-value" style="{"color:#fb8297" if tone=="red" else ""}">{value}</div>'
        f'<div class="pp-kpi-note">{html.escape(note)}</div></div>',
        unsafe_allow_html=True,
    )


def safe_num(value, default=0.0):
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def get_transactions():
    rows = db.q(
        "SELECT id, emp, category, amount, txn_date, has_receipt, approved "
        "FROM transactions ORDER BY txn_date DESC, id DESC"
    )
    return pd.DataFrame(
        rows,
        columns=["txn_id", "emp", "category", "amount", "txn_date", "has_receipt", "approved"],
    )


def risk_for_transaction(row, limit, duplicate=False):
    """Transparent rule-based risk score; no external model or schema changes."""
    amount = safe_num(row.get("amount"))
    limit = safe_num(limit)
    receipt = str(row.get("has_receipt", "N")).upper() in ("Y", "YES", "TRUE", "1")
    approved = str(row.get("approved", "N")).upper() in ("Y", "YES", "TRUE", "1")
    score = 8
    reasons = []
    if limit > 0 and amount > limit:
        over_pct = (amount / limit - 1) * 100
        score += min(48, 22 + over_pct * .45)
        reasons.append(f"Above policy limit by {over_pct:.0f}%")
    if not receipt and amount >= 500:
        score += 24
        reasons.append("Receipt missing")
    if not approved:
        score += 13
        reasons.append("Manager approval not recorded")
    if duplicate:
        score += 28
        reasons.append("Possible duplicate transaction")
    score = int(max(0, min(100, round(score))))
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return score, level, reasons


def build_risk_data(txns, rules):
    if txns.empty:
        return pd.DataFrame(columns=list(txns.columns) + ["limit", "risk_score", "risk_level", "risk_reasons"])
    dup_keys = set()
    try:
        for emp, cat, amount, txn_date, count in checks.duplicates():
            if int(count) > 1:
                dup_keys.add((str(emp), str(cat).lower(), round(safe_num(amount), 2), str(txn_date)))
    except Exception:
        pass
    records = []
    for _, source in txns.iterrows():
        row = source.to_dict()
        limit = rules.get(str(row["category"]).lower(), 0)
        key = (str(row["emp"]), str(row["category"]).lower(),
               round(safe_num(row["amount"]), 2), str(row["txn_date"]))
        score, level, reasons = risk_for_transaction(row, limit, key in dup_keys)
        row.update({"limit": limit, "risk_score": score, "risk_level": level,
                    "risk_reasons": "; ".join(reasons) if reasons else "No major risk signals"})
        records.append(row)
    return pd.DataFrame(records)


def make_simple_pdf(lines):
    """Create a compact, dependency-free PDF with ASCII-safe report text."""
    def pdf_escape(value):
        value = str(value).encode("ascii", "replace").decode("ascii")
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    pages = []
    page_lines = []
    for line in lines:
        wrapped = []
        text_line = str(line)
        while len(text_line) > 92:
            wrapped.append(text_line[:92])
            text_line = text_line[92:]
        wrapped.append(text_line)
        for part in wrapped:
            page_lines.append(part)
            if len(page_lines) >= 48:
                pages.append(page_lines)
                page_lines = []
    if page_lines or not pages:
        pages.append(page_lines)
    objects = []
    page_ids = []
    font_id = 3
    next_id = 4
    for page_lines in pages:
        content = ["BT", "/F1 10 Tf", "48 755 Td", "14 TL"]
        for i, line in enumerate(page_lines):
            if i:
                content.append("T*")
            content.append(f"({pdf_escape(line)}) Tj")
        content.append("ET")
        stream = "\n".join(content).encode("latin-1", "replace")
        page_id = next_id
        content_id = next_id + 1
        next_id += 2
        page_ids.append(page_id)
        objects.append((content_id, b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"))
        objects.append((page_id, f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>".encode()))
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    base = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    max_id = max([3] + [obj_id for obj_id, _ in objects])
    all_objects = {i + 1: obj for i, obj in enumerate(base)}
    for obj_id, obj in objects:
        all_objects[obj_id] = obj
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (max_id + 1)
    for obj_id in range(1, max_id + 1):
        obj = all_objects.get(obj_id, b"<< >>")
        offsets[obj_id] = len(output)
        output.extend(f"{obj_id} 0 obj\n".encode())
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {max_id + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for obj_id in range(1, max_id + 1):
        output.extend(f"{offsets[obj_id]:010d} 00000 n \n".encode())
    output.extend(
        f"trailer\n<< /Size {max_id + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    return bytes(output)


def audit_pdf_bytes(txns, risk_df, violations, truth, verification_rows):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "POLICYPULSE | EXPENSE COMPLIANCE AUDIT REPORT",
        f"Generated: {now}",
        "=" * 72,
        "EXECUTIVE SUMMARY",
        f"Transactions reviewed: {len(txns)}",
        f"Policy violations: {len(violations)}",
        f"Total spend: {money(txns['amount'].sum()) if not txns.empty else money(0)}",
        f"Total overspend: {money(truth.get('overspend', 0))}",
        f"Possible duplicates: {truth.get('duplicates', 0)}",
        f"Missing receipts: {len(checks.missing_receipts())}",
        "",
        "RISK OVERVIEW",
    ]
    if not risk_df.empty:
        lines += [
            f"High risk: {int((risk_df['risk_level']=='HIGH').sum())}",
            f"Medium risk: {int((risk_df['risk_level']=='MEDIUM').sum())}",
            f"Low risk: {int((risk_df['risk_level']=='LOW').sum())}",
        ]
    lines += ["", "POLICY VIOLATIONS"]
    if violations:
        for item in violations[:100]:
            lines.append(
                f"#{item.get('txn_id')} | {item.get('emp')} | {item.get('category')} | "
                f"Amount {money(item.get('amount'))} | Limit {money(item.get('limit'))}"
            )
    else:
        lines.append("No policy violations returned by the existing checks module.")
    lines += ["", "RECENT AI VERIFICATION RESULTS"]
    if verification_rows:
        for item in verification_rows[:30]:
            lines.append(
                f"{item[1]} | AI {item[2]} | Db2 {item[3]} | {item[4]}"
            )
    else:
        lines.append("No verification history available.")
    lines += ["", "NOTE", "Risk scores are transparent rule-based indicators, not a fraud determination.",
              "This report reflects records available in Db2 at generation time."]
    return make_simple_pdf(lines)


# -------------------- Header and data --------------------

ai_label = "watsonx.ai" if llm.available() else "Simulated AI"
st.markdown(
    f'<div class="pp-header"><div class="pp-brand"><div class="pp-logo">🛡️</div>'
    f'<div><div class="pp-name">PolicyPulse</div>'
    f'<div class="pp-sub">Expense intelligence · Policy compliance · Verified by IBM Db2</div></div></div>'
    f'<div class="pp-status"><span class="pp-pill"><span class="pp-dot"></span> Db2 connected</span>'
    f'<span class="pp-pill">✦ {html.escape(ai_label)}</span></div></div>',
    unsafe_allow_html=True,
)

if "flash" in st.session_state:
    kind, msg = st.session_state.pop("flash")
    getattr(st, kind, st.info)(msg)

with st.sidebar:
    st.markdown("## 🛡️ PolicyPulse")
    st.caption("ENTERPRISE EXPENSE INTELLIGENCE")
    st.markdown("---")
    st.markdown("**Platform status**")
    st.success("Database connection active")
    st.info(f"AI engine: {ai_label}")
    try:
        n_clauses = db.q("SELECT COUNT(*) FROM policy_clauses")[0][0]
        st.metric("Policy clauses indexed", n_clauses)
    except Exception as exc:
        st.warning(f"Policy index unavailable: {exc}")
    st.markdown("---")
    st.caption("Powered by IBM Db2 · SQL rules · Vector search · AI claim verification")
    st.caption("Risk indicators are decision-support signals, not fraud findings.")

tabs = st.tabs([
    "◈ Overview",
    "◎ Risk Radar",
    "⌁ Policy Simulator",
    "▤ Policy & Rules",
    "⚑ Violations",
    "✦ AI Auditor",
    "◷ Activity",
    "♙ Leaderboard",
    "♡ Data Health",
])


# -------------------- Load current Db2 data for analytics --------------------
txns = get_transactions()
rule_rows = db.q("SELECT category, limit_amt FROM rules ORDER BY category")
rule_map = {str(cat).lower(): safe_num(limit) for cat, limit in rule_rows}
risk_df = build_risk_data(txns, rule_map)
violations = checks.violations()
truth = verifier.ground_truth()


# -------------------- Overview --------------------

with tabs[0]:
    st.markdown('<div class="page-kicker">EXECUTIVE OVERVIEW</div><div class="page-title">Expense intelligence, at a glance.</div>'
                '<div class="page-desc">A live view of policy compliance, financial exposure and AI verification.</div>',
                unsafe_allow_html=True)
    total = len(txns)
    spend = safe_num(txns["amount"].sum()) if not txns.empty else 0
    violation_count = len(violations)
    compliance = max(0, 100 * (1 - violation_count / total)) if total else 100
    high_risk = int((risk_df["risk_level"] == "HIGH").sum()) if not risk_df.empty else 0

    cols = st.columns(4, gap="medium")
    with cols[0]:
        kpi("Transactions", f"{total:,}", "All submitted expenses", "▤")
    with cols[1]:
        kpi("Total spend", money(spend), "Across all categories", "₹")
    with cols[2]:
        kpi("Policy violations", f"{violation_count:,}", "Returned by compliance checks", "⚑", "red" if violation_count else "")
    with cols[3]:
        kpi("High-risk expenses", f"{high_risk:,}", "Risk radar indicators", "◉", "red" if high_risk else "")

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.markdown(
            f'<div class="pp-hero"><div class="pp-hero-label">OVERALL COMPLIANCE RATE</div>'
            f'<div class="pp-hero-value">{compliance:.1f}<span>%</span></div>'
            f'<div class="pp-hero-note">{total-violation_count:,} compliant · {violation_count:,} flagged · Overspend {money(truth.get("overspend",0))}</div>'
            f'<div class="pp-hero-track"><span style="width:{compliance:.1f}%"></span></div></div>',
            unsafe_allow_html=True,
        )
    with right:
        with st.container(border=True):
            section("Financial exposure", "Current Db2 snapshot")
            kpi("Total overspend", money(truth.get("overspend", 0)), "Amount above policy limits", "↗", "red")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Possible duplicates", int(truth.get("duplicates", 0)))
            with c2:
                st.metric("Missing receipts", len(checks.missing_receipts()))

    lower_left, lower_right = st.columns(2, gap="large")
    by_cat = db.q("SELECT category, COUNT(*) FROM v_violations GROUP BY category")
    with lower_left:
        with st.container(border=True):
            section("Violations by category", "Db2 compliance view")
            if by_cat:
                st.bar_chart(pd.DataFrame(by_cat, columns=["Category", "Violations"]).set_index("Category"), height=260)
            else:
                st.success("No policy violations in the current view.")
    by_emp = db.q("SELECT emp, SUM(amount - limit_amt) FROM v_violations GROUP BY emp ORDER BY 2 DESC")
    with lower_right:
        with st.container(border=True):
            section("Overspend by employee", "Amount above limit")
            if by_emp:
                df_emp = pd.DataFrame(by_emp, columns=["Employee", "Overspend"])
                df_emp["Overspend"] = pd.to_numeric(df_emp["Overspend"], errors="coerce").fillna(0)
                st.bar_chart(df_emp.set_index("Employee"), height=260)
            else:
                st.caption("No overspend data to chart.")

    with st.container(border=True):
        section("Highest risk expenses", "Top five rule-based indicators")
        if risk_df.empty:
            st.caption("No transactions available.")
        else:
            for _, r in risk_df.sort_values("risk_score", ascending=False).head(5).iterrows():
                color = "#fb7185" if r["risk_level"] == "HIGH" else "#fbbf65" if r["risk_level"] == "MEDIUM" else "#38d9a9"
                st.markdown(
                    f'<div class="pp-risk"><div style="width:135px;font-size:.78rem;color:#dce6f8;font-weight:700;">'
                    f'{html.escape(str(r["emp"]))} · {html.escape(str(r["category"]).title())}</div>'
                    f'<div class="pp-risk-track"><span style="width:{int(r["risk_score"])}%;background:{color};"></span></div>'
                    f'<div style="width:45px;text-align:right;font-size:.78rem;color:{color};font-weight:800;">{int(r["risk_score"])}</div></div>',
                    unsafe_allow_html=True,
                )


# -------------------- AI Expense Risk Radar --------------------

with tabs[1]:
    st.markdown('<div class="page-kicker">PROACTIVE CONTROL</div><div class="page-title">AI Expense Risk Radar</div>'
                '<div class="page-desc">Prioritize expenses using transparent, explainable risk signals calculated from existing Db2 records.</div>',
                unsafe_allow_html=True)
    if risk_df.empty:
        st.info("No transactions available for risk analysis.")
    else:
        high = int((risk_df["risk_level"] == "HIGH").sum())
        medium = int((risk_df["risk_level"] == "MEDIUM").sum())
        low = int((risk_df["risk_level"] == "LOW").sum())
        a, b, c, d = st.columns(4)
        with a: kpi("High risk", high, "Score 70–100", "🔴", "red")
        with b: kpi("Medium risk", medium, "Score 40–69", "🟠")
        with c: kpi("Low risk", low, "Score 0–39", "🟢")
        with d: kpi("Average risk", f'{risk_df["risk_score"].mean():.1f}/100', "Across all expenses", "◉")

        f1, f2 = st.columns([1, 2])
        with f1:
            risk_filter = st.selectbox("Risk level", ["All", "HIGH", "MEDIUM", "LOW"])
        with f2:
            employee_filter = st.selectbox("Employee", ["All"] + sorted(risk_df["emp"].dropna().astype(str).unique().tolist()))
        view = risk_df.copy()
        if risk_filter != "All":
            view = view[view["risk_level"] == risk_filter]
        if employee_filter != "All":
            view = view[view["emp"].astype(str) == employee_filter]
        show_cols = ["txn_id", "emp", "category", "amount", "limit", "risk_score", "risk_level", "risk_reasons"]
        st.dataframe(view[show_cols].sort_values("risk_score", ascending=False), use_container_width=True, hide_index=True)

        st.markdown("---")
        section("Investigate a risk signal", "Select an expense to inspect its evidence")
        options = view["txn_id"].tolist()
        if options:
            selected = st.selectbox("Transaction", options, format_func=lambda x: f"#{x}")
            selected_row = view[view["txn_id"] == selected].iloc[0]
            score = int(selected_row["risk_score"])
            level = selected_row["risk_level"]
            color = "#fb7185" if level == "HIGH" else "#fbbf65" if level == "MEDIUM" else "#38d9a9"
            st.markdown(
                f'<div class="pp-callout"><b style="color:{color}">{level} RISK · {score}/100</b><br>'
                f'{html.escape(str(selected_row["risk_reasons"]))}<br>'
                f'Employee: {html.escape(str(selected_row["emp"]))} · Category: {html.escape(str(selected_row["category"]))} · '
                f'Amount: {money(selected_row["amount"])} · Policy limit: {money(selected_row["limit"])}</div>',
                unsafe_allow_html=True,
            )
            st.caption("Scoring logic: policy overspend, missing receipt (₹500+), missing manager approval and possible duplicate. This is a transparent heuristic, not an ML fraud verdict.")
        else:
            st.caption("No expenses match these filters.")


# -------------------- Policy Impact Simulator --------------------

with tabs[2]:
    st.markdown('<div class="page-kicker">WHAT-IF ANALYSIS</div><div class="page-title">Policy Impact Simulator</div>'
                '<div class="page-desc">Explore alternative policy limits safely. Simulation is read-only and does not update Db2.</div>',
                unsafe_allow_html=True)
    if txns.empty or not rule_map:
        st.info("Upload a policy and ensure transactions exist to use the simulator.")
    else:
        with st.container(border=True):
            section("Choose a policy scenario", "Changes apply only to this simulation")
            categories = sorted(rule_map.keys())
            selected_cat = st.selectbox("Expense category", categories, key="sim_category")
            current_limit = rule_map[selected_cat]
            new_limit = st.number_input("Proposed limit (₹)", min_value=0.0, value=float(current_limit), step=100.0, key="sim_limit")
            cat_txns = txns[txns["category"].astype(str).str.lower() == selected_cat].copy()
            old_violations = int((pd.to_numeric(cat_txns["amount"], errors="coerce") > current_limit).sum())
            new_violations = int((pd.to_numeric(cat_txns["amount"], errors="coerce") > new_limit).sum())
            old_over = (pd.to_numeric(cat_txns["amount"], errors="coerce") - current_limit).clip(lower=0).sum()
            new_over = (pd.to_numeric(cat_txns["amount"], errors="coerce") - new_limit).clip(lower=0).sum()
            delta_v = new_violations - old_violations
            delta_over = new_over - old_over
            x1, x2, x3 = st.columns(3)
            with x1: kpi("Current limit", money(current_limit), selected_cat.title(), "◈")
            with x2: kpi("Proposed limit", money(new_limit), "Simulation only", "✎")
            with x3: kpi("Projected violations", f"{new_violations}", f"{delta_v:+d} vs current", "⚑", "red" if delta_v > 0 else "")
            y1, y2 = st.columns(2)
            with y1: st.metric("Current overspend exposure", money(old_over))
            with y2: st.metric("Projected overspend exposure", money(new_over), delta=money(-delta_over) + " vs current" if delta_over <= 0 else "+" + money(delta_over))
            if delta_v < 0 or delta_over < 0:
                st.success("This scenario reduces at least one measured exposure for this category.")
            elif delta_v > 0 or delta_over > 0:
                st.warning("This scenario increases the measured exposure for this category.")
            else:
                st.info("This scenario does not change the measured violation or overspend totals.")
            st.caption("The simulation compares transaction amounts against the proposed category limit. Receipt and approval checks remain governed by the existing compliance logic.")
            if st.button("Reset to current policy limit"):
                st.session_state["sim_limit"] = float(current_limit)
                st.rerun()


# -------------------- Policy & Rules --------------------

with tabs[3]:
    st.markdown('<div class="page-kicker">POLICY KNOWLEDGE BASE</div><div class="page-title">Policy & Rules</div>'
                '<div class="page-desc">Upload policy documents, manage category limits and retrieve relevant clauses through Db2 vector search.</div>',
                unsafe_allow_html=True)
    with st.container(border=True):
        section("Policy document", "PDF → clauses → embeddings → Db2")
        pdf = st.file_uploader("Upload a policy PDF", type="pdf", label_visibility="collapsed")
        if pdf and st.button("Process policy document", type="primary"):
            with st.spinner("Extracting clauses, creating embeddings and saving to Db2..."):
                n_clauses, n_rules = ingest.load_policy(pdf, pdf.name)
            st.session_state["flash"] = ("success", f"{n_clauses} clauses stored as vectors; {n_rules} rules extracted.")
            st.rerun()

    rules = db.q("SELECT category, limit_amt FROM rules ORDER BY category")
    with st.container(border=True):
        section("Policy limits", "Edit limits and save to Db2")
        if rules:
            cols = st.columns(min(len(rules), 4))
            new_limits = {}
            for i, (cat, lim) in enumerate(rules):
                with cols[i % len(cols)]:
                    new_limits[cat] = st.number_input(f"{str(cat).title()} (₹)", value=float(lim), step=100.0, key=f"limit_{cat}")
            if st.button("Save policy limits", type="primary"):
                for cat, value in new_limits.items():
                    db.q("UPDATE rules SET limit_amt = ? WHERE category = ?", (value, cat))
                st.session_state["flash"] = ("success", "Policy limits updated in Db2.")
                st.rerun()
        else:
            st.caption("No rules found. Upload a policy PDF to extract rules.")

    with st.container(border=True):
        section("Ask the policy", "Semantic retrieval · Db2 vector search")
        question = st.text_input("Ask a question about your expense policy", placeholder="e.g. Do I need approval for a taxi ride?")
        if question:
            for page, body, dist in checks.search(question, 3):
                st.markdown(
                    f'<div class="pp-clause"><span class="pp-tag">Page {page}</span> '
                    f'<span class="pp-tag green">Distance {safe_num(dist):.3f}</span><br><br>{html.escape(str(body))}</div>',
                    unsafe_allow_html=True,
                )


# -------------------- Violations --------------------

with tabs[4]:
    st.markdown('<div class="page-kicker">COMPLIANCE EXCEPTIONS</div><div class="page-title">Policy Violations</div>'
                '<div class="page-desc">Review, investigate and record expense exceptions with the existing Db2 compliance checks.</div>',
                unsafe_allow_html=True)
    vs = checks.violations()
    with st.container(border=True):
        section("Violation register", "Audit-ready exception list")
        if not vs:
            st.success("No violations found by the current compliance view.")
        else:
            df = pd.DataFrame(vs)
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
            df["limit"] = pd.to_numeric(df["limit"], errors="coerce").fillna(0)
            df["over_by_%"] = ((df["amount"] / df["limit"].replace(0, pd.NA) - 1) * 100).round(0)
            st.dataframe(df.drop(columns=["clause_id"], errors="ignore"), use_container_width=True, hide_index=True)
            st.download_button("Download violations CSV", df.to_csv(index=False), "policypulse_violations.csv", mime="text/csv")

    if vs:
        with st.container(border=True):
            section("Inspect a violation", "Retrieve supporting policy evidence")
            df = pd.DataFrame(vs)
            pick = st.selectbox("Transaction to inspect", df["txn_id"].tolist(), format_func=lambda x: f"Transaction #{x}")
            row = df[df["txn_id"] == pick].iloc[0]
            # Existing checks.best_clause interface takes category and limit (two arguments).
            page, body = checks.best_clause(row["category"], row["limit"])
            over_pct = ((safe_num(row["amount"]) / safe_num(row["limit"]) - 1) * 100) if safe_num(row["limit"]) else 0
            st.markdown(
                f'<div class="pp-clause"><span class="pp-tag">Policy page {page}</span> '
                f'<span class="pp-tag red">{html.escape(str(row["category"]).title())} · {over_pct:.0f}% over</span>'
                f'<br><br>{html.escape(str(body))}</div>',
                unsafe_allow_html=True,
            )

    with st.expander("＋ Submit a new expense", expanded=False):
        cats = [r[0] for r in db.q("SELECT category FROM rules")]
        if not cats:
            st.warning("Add policy rules before submitting an expense.")
        else:
            a, b, c = st.columns(3)
            with a: emp = st.text_input("Employee", "Aarav")
            with b: cat = st.selectbox("Category", cats)
            with c: amt = st.number_input("Amount (₹)", min_value=0.0, value=2500.0, step=100.0)
            d, e = st.columns(2)
            with d: receipt = st.checkbox("Receipt attached", True)
            with e: approved = st.checkbox("Approved by manager", False)
            if st.button("Submit expense to Db2", type="primary"):
                new_id = db.q("SELECT COALESCE(MAX(id), 0) + 1 FROM transactions")[0][0]
                db.q("INSERT INTO transactions VALUES (?, ?, ?, ?, CURRENT DATE, ?, ?)",
                     (new_id, emp, cat, amt, "Y" if receipt else "N", "Y" if approved else "N"))
                hit = db.q("SELECT limit_amt FROM v_violations WHERE txn_id = ?", (new_id,))
                st.session_state["flash"] = (
                    "error" if hit else "success",
                    f"Expense #{new_id} violates policy (limit {money(hit[0][0])})." if hit else f"Expense #{new_id} submitted and appears compliant."
                )
                st.rerun()


# -------------------- AI Auditor / Explainable Verification --------------------

with tabs[5]:
    st.markdown('<div class="page-kicker">TRUST & VERIFICATION</div><div class="page-title">Explainable AI Auditor</div>'
                '<div class="page-desc">AI may explain the numbers. Db2 independently checks the claims against stored records.</div>',
                unsafe_allow_html=True)
    with st.container(border=True):
        section("Step 1 · Generate an AI explanation", "Generate or edit the model response")
        st.session_state.setdefault("ai_text", "")
        c1, c2 = st.columns([1, 3])
        with c1:
            sim = st.checkbox("Simulate hallucination", help="Intentionally changes demo claims to test the verifier.")
            if st.button("Generate AI summary", type="primary"):
                with st.spinner("Generating explanation..."):
                    st.session_state["ai_text"] = llm.summarize(sim)
        with c2:
            st.text_area("AI explanation", key="ai_text", height=125, placeholder="Generate a summary or paste an AI-generated explanation here.")

    with st.container(border=True):
        section("Step 2 · Verify every numeric claim", "Db2 is the source of truth")
        if st.button("Verify claims with Db2", type="primary"):
            result = verifier.verify(st.session_state.get("ai_text", ""))
            st.session_state["last_verification"] = result
            if not result:
                st.warning("No numeric claims found in the text.")
            else:
                bad = sum(r["status"] == "UNVERIFIED" for r in result)
                if bad:
                    st.error(f"{len(result)-bad} of {len(result)} claims verified · {bad} unverified")
                else:
                    st.success(f"All {len(result)} numeric claims verified by Db2.")
        for r in st.session_state.get("last_verification", []):
            ok = r["status"] == "VERIFIED"
            status_class = "green" if ok else "red"
            st.markdown(
                f'<div class="pp-claim"><div class="pp-claim-head"><div class="pp-claim-name">{html.escape(str(r["claim"]))}</div>'
                f'<span class="pp-tag {status_class}">{r["status"]}</span></div>'
                f'<div class="pp-claim-values">AI stated <b>{safe_num(r["AI said"]):g}</b> &nbsp;·&nbsp; '
                f'Db2 returned <b>{safe_num(r["Db2 says"]):g}</b></div></div>',
                unsafe_allow_html=True,
            )
            with st.expander(f"SQL evidence · {r['claim']}"):
                st.code(verifier.SQL[r["claim"]], language="sql")
        if st.session_state.get("last_verification"):
            st.markdown('<div class="pp-callout">Verification principle: AI output is treated as an untrusted claim. The displayed status comes from the existing verifier result, not from the language model itself.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        section("Verification audit trail", "Most recent Db2 verification records")
        verifier.ensure_log()
        log = db.q("SELECT ts, claim, ai_value, db2_value, status FROM verification_log ORDER BY ts DESC LIMIT 20")
        if log:
            st.dataframe(pd.DataFrame(log, columns=["Time", "Claim", "AI value", "Db2 value", "Status"]), use_container_width=True, hide_index=True)
        else:
            st.caption("No verification history yet.")


# -------------------- Live Activity Feed --------------------

with tabs[6]:
    st.markdown('<div class="page-kicker">OPERATIONAL MONITORING</div><div class="page-title">Live Activity Feed</div>'
                '<div class="page-desc">Recent expense submissions and AI verification events read directly from Db2.</div>',
                unsafe_allow_html=True)
    if st.button("↻ Refresh activity"):
        st.rerun()
    events = []
    try:
        recent_txns = db.q("SELECT id, emp, category, amount, txn_date, has_receipt, approved FROM transactions ORDER BY txn_date DESC, id DESC FETCH FIRST 15 ROWS ONLY")
        for item in recent_txns:
            txn_id, emp, category, amount, txn_date, receipt, approved = item
            events.append((str(txn_date), int(txn_id), "EXPENSE", f"{emp} submitted {category} expense", f"{money(amount)} · Receipt {receipt} · Approval {approved}"))
    except Exception:
        # Fallback for Db2 drivers/configurations that support LIMIT syntax.
        recent_txns = db.q("SELECT id, emp, category, amount, txn_date, has_receipt, approved FROM transactions ORDER BY txn_date DESC, id DESC LIMIT 15")
        for item in recent_txns:
            txn_id, emp, category, amount, txn_date, receipt, approved = item
            events.append((str(txn_date), int(txn_id), "EXPENSE", f"{emp} submitted {category} expense", f"{money(amount)} · Receipt {receipt} · Approval {approved}"))
    try:
        recent_logs = db.q("SELECT ts, claim, ai_value, db2_value, status FROM verification_log ORDER BY ts DESC FETCH FIRST 15 ROWS ONLY")
    except Exception:
        try:
            recent_logs = db.q("SELECT ts, claim, ai_value, db2_value, status FROM verification_log ORDER BY ts DESC LIMIT 15")
        except Exception:
            recent_logs = []
    for i, item in enumerate(recent_logs):
        ts, claim, ai_value, db2_value, status = item
        events.append((str(ts), 1000000 + i, "VERIFICATION", f"AI claim checked: {claim}", f"AI {ai_value} · Db2 {db2_value} · {status}"))
    events.sort(key=lambda x: (x[0], x[1]), reverse=True)
    with st.container(border=True):
        section("Recent events", f"{len(events)} events loaded")
        if not events:
            st.caption("No recent activity available.")
        for timestamp, event_id, kind, title, detail in events[:25]:
            tag = "green" if kind == "VERIFICATION" and "VERIFIED" in detail else "amber" if kind == "VERIFICATION" else ""
            icon = "✦" if kind == "VERIFICATION" else "₹"
            st.markdown(
                f'<div class="pp-row"><div class="pp-avatar">{icon}</div><div class="pp-row-main">'
                f'<div class="pp-row-name">{html.escape(title)}</div>'
                f'<div class="pp-row-meta">{html.escape(timestamp)} · {html.escape(detail)}</div></div>'
                f'<span class="pp-tag {tag}">{kind}</span></div>',
                unsafe_allow_html=True,
            )
    st.caption("The feed reflects recent records available in the database; it refreshes when the page reruns.")


# -------------------- Employee Compliance Leaderboard --------------------

with tabs[7]:
    st.markdown('<div class="page-kicker">PEOPLE & PERFORMANCE</div><div class="page-title">Employee Compliance Leaderboard</div>'
                '<div class="page-desc">Compare employee expense patterns using transparent transaction and risk indicators.</div>',
                unsafe_allow_html=True)
    if risk_df.empty:
        st.info("No transaction data available.")
    else:
        leaderboard = risk_df.groupby("emp", dropna=False).agg(
            transactions=("txn_id", "count"),
            total_spend=("amount", "sum"),
            avg_risk=("risk_score", "mean"),
            high_risk=("risk_level", lambda s: int((s == "HIGH").sum())),
            medium_risk=("risk_level", lambda s: int((s == "MEDIUM").sum())),
        ).reset_index()
        # Compliance score is a transparent inverse of average risk, not a disciplinary rating.
        leaderboard["compliance_score"] = (100 - leaderboard["avg_risk"]).clip(0, 100).round(1)
        leaderboard = leaderboard.sort_values(["compliance_score", "transactions"], ascending=[False, False])
        best = leaderboard.iloc[0]
        a, b, c = st.columns(3)
        with a: kpi("Employees analyzed", len(leaderboard), "Distinct employee names", "♙")
        with b: kpi("Top compliance score", f'{best["compliance_score"]:.1f}/100', str(best["emp"]), "🏆")
        with c: kpi("Employees with high-risk items", int((leaderboard["high_risk"] > 0).sum()), "At least one high-risk expense", "◉")
        display = leaderboard.rename(columns={
            "emp": "Employee", "transactions": "Transactions", "total_spend": "Total spend",
            "avg_risk": "Average risk", "high_risk": "High risk items",
            "medium_risk": "Medium risk items", "compliance_score": "Indicative compliance score",
        })
        st.dataframe(display, use_container_width=True, hide_index=True)
        with st.container(border=True):
            section("Employee comparison", "Indicative compliance score")
            chart = leaderboard[["emp", "compliance_score"]].set_index("emp").sort_values("compliance_score")
            st.bar_chart(chart, height=300)
        st.caption("Leaderboard scores are derived from the rule-based risk indicators shown in Risk Radar. They are intended for policy coaching, not employee performance evaluation.")


# -------------------- Data Health --------------------

with tabs[8]:
    st.markdown('<div class="page-kicker">DATA QUALITY & CONTROL</div><div class="page-title">Data Health</div>'
                '<div class="page-desc">Identify duplicate claims and missing receipt evidence in the current Db2 records.</div>',
                unsafe_allow_html=True)
    dups = checks.duplicates()
    miss = checks.missing_receipts()
    a, b, c = st.columns(3)
    with a: kpi("Possible duplicates", len(dups), "Same employee, category, amount and date", "⧉", "red" if dups else "")
    with b: kpi("Missing receipts", len(miss), "Claims without receipt (₹500+)", "▧", "red" if miss else "")
    with c: kpi("Policy clauses", db.q("SELECT COUNT(*) FROM policy_clauses")[0][0], "Indexed policy evidence", "▤")
    with st.container(border=True):
        section("Duplicate transactions", "Potential repeated expense claims")
        if dups:
            st.dataframe(pd.DataFrame(dups, columns=["Employee", "Category", "Amount", "Date", "Count"]), use_container_width=True, hide_index=True)
        else:
            st.success("No possible duplicates detected.")
    with st.container(border=True):
        section("Missing receipts", "Transactions above the configured threshold")
        if miss:
            st.dataframe(pd.DataFrame(miss, columns=["ID", "Employee", "Category", "Amount"]), use_container_width=True, hide_index=True)
        else:
            st.success("No missing receipts detected.")


# -------------------- One-click Audit Report --------------------
# Kept at the end of the page so users can export a consistent snapshot.
st.markdown("---")
with st.container(border=True):
    section("Executive audit export", "Generate a downloadable snapshot from current Db2 records")
    st.markdown(
        '<div class="pp-callout">Creates a compact PDF containing the executive summary, policy exceptions, '
        'risk overview and recent AI verification history. The report is generated locally and does not change Db2.</div>',
        unsafe_allow_html=True,
    )
    if st.button("Generate audit PDF", type="primary"):
        verifier.ensure_log()
        try:
            export_logs = db.q("SELECT ts, claim, ai_value, db2_value, status FROM verification_log ORDER BY ts DESC LIMIT 30")
        except Exception:
            export_logs = []
        pdf_data = audit_pdf_bytes(txns, risk_df, violations, truth, export_logs)
        st.download_button(
            "⬇ Download PolicyPulse Audit Report",
            data=pdf_data,
            file_name=f"PolicyPulse_Audit_{date.today().isoformat()}.pdf",
            mime="application/pdf",
        )
