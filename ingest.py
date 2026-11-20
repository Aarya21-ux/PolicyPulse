import re
from pypdf import PdfReader
import db
from embed import vec

CATEGORIES = ["meals", "travel", "hotel", "cab", "gifts", "fuel"]
AMT = re.compile(r"(?:Rs\.?|INR|₹)\s?([\d,]+)", re.I)

def split_clauses(file):
    out = []
    for pno, page in enumerate(PdfReader(file).pages, 1):
        for chunk in re.split(r"\n\s*\n|(?<=\.)\s+(?=[A-Z0-9])", page.extract_text() or ""):
            chunk = " ".join(chunk.split())
            if len(chunk) > 30:
                out.append((pno, chunk[:1900]))
    return out

def pull_rule(text):
    low = text.lower()
    amt = AMT.search(text)
    cat = next((c for c in CATEGORIES if c in low), None)
    if cat and amt:
        return cat, float(amt.group(1).replace(",", ""))
    return None

def load_policy(file, name):
    db.q("DELETE FROM rules")
    db.q("DELETE FROM policy_clauses")
    n_rules = 0
    seen = set()  # ek category ka ek hi rule
    clauses = split_clauses(file)
    for pno, body in clauses:
        db.q("INSERT INTO policy_clauses (source, page, body, emb) "
             "VALUES (?, ?, ?, VECTOR(?, 384, FLOAT32))", (name, pno, body, vec(body)))
        rule = pull_rule(body)
        if rule and rule[0] not in seen:
            seen.add(rule[0])
            cid = db.q("SELECT MAX(id) FROM policy_clauses")[0][0]
            db.q("INSERT INTO rules (category, limit_amt, clause_id) VALUES (?, ?, ?)",
                 (rule[0], rule[1], cid))
            n_rules += 1
    return len(clauses), n_rules
