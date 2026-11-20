import threading

_model = None
_lock = threading.Lock()

def vec(text):
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                # heavy import yahin karte hain taaki app jaldi open ho
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dims
    v = _model.encode(text)
    return "[" + ",".join(f"{x:.5f}" for x in v) + "]"