import re
import db

# har claim type ka apna SQL (UI me bhi dikhate hain)
SQL = {
    "violations": "SELECT COUNT(*) FROM v_violations",
    "overspend": "SELECT COALESCE(SUM(amount - limit_amt), 0) FROM v_violations",
    "duplicates": "SELECT COUNT(*) FROM (SELECT 1 FROM transactions "
                  "GROUP BY emp, category, amount, txn_date HAVING COUNT(*) > 1)",
}

# AI ke text se number nikalne ke patterns
PATTERNS = {
    "violations": r"(\d+)\s+violations?",
    "overspend": r"overspend[^\d]{0,20}([\d,]+(?:\.\d+)?)",
    "duplicates": r"(\d+)\s+duplicates?",
}

_log_ready = False

def ensure_log():
    global _log_ready
    if _log_ready:
        return
    try:
        db.q("CREATE TABLE verification_log (id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, "
             "ts TIMESTAMP DEFAULT CURRENT TIMESTAMP, claim VARCHAR(30), "
             "ai_value DECIMAL(14,2), db2_value DECIMAL(14,2), status VARCHAR(12))")
    except Exception:
        pass  # table pehle se hai
    _log_ready = True

def ground_truth():
    return {k: float(db.q(sql)[0][0]) for k, sql in SQL.items()}

def verify(ai_text):
    ensure_log()
    truth = ground_truth()
    results = []
    for key, pat in PATTERNS.items():
        for m in re.finditer(pat, ai_text, re.I):
            claimed = float(m.group(1).replace(",", ""))
            ok = abs(claimed - truth[key]) < 0.01
            status = "VERIFIED" if ok else "UNVERIFIED"
            results.append({"claim": key, "ai": claimed, "db2": truth[key], "status": status})
            db.q("INSERT INTO verification_log (claim, ai_value, db2_value, status) "
                 "VALUES (?, ?, ?, ?)", (key, claimed, truth[key], status))
    return results