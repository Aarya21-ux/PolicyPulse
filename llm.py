import os
import db
import verifier

def available():
    return bool(os.getenv("WATSONX_APIKEY") and os.getenv("WATSONX_PROJECT_ID"))

def _ask_watsonx(prompt):
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    model = ModelInference(
        model_id=os.getenv("WATSONX_MODEL", "ibm/granite-3-8b-instruct"),
        credentials=Credentials(url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
                                api_key=os.getenv("WATSONX_APIKEY")),
        project_id=os.getenv("WATSONX_PROJECT_ID"),
        params={"max_new_tokens": 150, "temperature": 0.7},
    )
    return model.generate_text(prompt=prompt).strip()

def summarize(simulate_error=False):
    if available():
        # LLM ko sirf raw rows dete hain, totals khud nikalne padenge (yahin galti hoti hai)
        rows = db.q("SELECT txn_id, category, amount, limit_amt FROM v_violations")
        lines = "\n".join(f"{r[0]}: {r[1]} amount={r[2]} limit={r[3]}" for r in rows)
        prompt = ("Below are expense policy violations. Reply in ONE sentence exactly like: "
                  "'There are N violations with a total overspend of Rs X.' "
                  "(overspend = amount minus limit, summed).\n" + lines)
        return _ask_watsonx(prompt)
    t = verifier.ground_truth()
    n, over = t["violations"], t["overspend"]
    if simulate_error:
        n, over = n + 3, over * 1.18
    return f"There are {int(n)} violations with a total overspend of Rs {over:.0f}."