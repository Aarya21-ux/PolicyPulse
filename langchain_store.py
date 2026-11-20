
import json
import hashlib

import db
from embed import vec
from langchain_db2 import DB2VS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document


class PolicyEmbeddings(Embeddings):

    def embed_documents(self, texts):
        return [json.loads(vec(text)) for text in texts]

    def embed_query(self, text):
        return json.loads(vec(text))


_store = None
_indexed = False


def get_store():
    global _store

    if _store is None:
        _store = DB2VS(
            embedding_function=PolicyEmbeddings(),
            table_name="POLICYPULSE_LC_VECTORS",
            client=db.conn()
        )

    return _store


def search_policy(query, top_k=3):
    global _indexed

    store = get_store()

    if not _indexed:

        # Get IDs already present in the LangChain vector table
        existing = set(store.get_pks())

        # Read policy clauses from the main Db2 table
        rows = db.q(
            "SELECT id, page, body FROM policy_clauses"
        )

        docs = []
        ids = []

        for clause_id, page, body in rows:

            # LangChain DB2VS hashes IDs before storing them
            hashed_id = hashlib.sha256(
                str(clause_id).encode()
            ).hexdigest()[:16].upper()

            # Insert only clauses that are not already indexed
            if hashed_id not in existing:

                docs.append(
                    Document(
                        page_content=body,
                        metadata={
                            "clause_id": str(clause_id),
                            "page": page
                        }
                    )
                )

                ids.append(str(clause_id))

        if docs:
            store.add_documents(docs, ids=ids)

        _indexed = True

    # Search using LangChain DB2 vector store
    results = store.similarity_search(
        query,
        k=top_k
    )

    return [
        (
            doc.metadata.get("page"),
            doc.page_content,
            0.0
        )
        for doc in results
    ]
