
import db
import langchain_store


def violations():
    rows = db.q(
        "SELECT txn_id, emp, category, amount, limit_amt, clause_id "
        "FROM v_violations ORDER BY amount DESC"
    )

    return [
        dict(
            zip(
                ["txn_id", "emp", "category", "amount", "limit", "clause_id"],
                row
            )
        )
        for row in rows
    ]


def best_clause(category, amount, limit=None):
    if limit is not None:
        lim_str = f"{limit:.0f}"
    else:
        lim_str = "0"

    query = f"{category} expense above Rs {lim_str} needs approval"

    results = langchain_store.search_policy(query, top_k=1)

    if results:
        page, body, score = results[0]
        return page, body

    return None, "no clause found"


def duplicates():
    return db.q(
        "SELECT emp, category, amount, txn_date, COUNT(*) "
        "FROM transactions "
        "GROUP BY emp, category, amount, txn_date "
        "HAVING COUNT(*) > 1"
    )


def missing_receipts(min_amt=500):
    return db.q(
        "SELECT id, emp, category, amount FROM transactions "
        "WHERE has_receipt = 'N' AND amount >= ?",
        (min_amt,)
    )


def search(query_text, top_k=3):
    return langchain_store.search_policy(
        query=query_text,
        top_k=top_k
    )
