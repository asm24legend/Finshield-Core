import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "api"))

import ollama
from sqlalchemy import text


def embed_query(query_text: str) -> list[float]:
    """Embeds a query string the same way regulation chunks were embedded —
    using the same model is essential, since vectors from different models
    aren't comparable."""
    response = ollama.embeddings(model="nomic-embed-text", prompt=query_text)
    return response["embedding"]


def find_relevant_regulations(db, query_text: str, top_k: int = 3) -> list[dict]:
    """
    Finds the most semantically similar regulation chunks to the given query
    text, using pgvector's cosine distance operator (<=>).

    Lower distance = more similar. We convert to a 0-1 "relevance" score
    (1 - distance) so it reads more intuitively in the output.
    """
    query_embedding = embed_query(query_text)

    result = db.execute(
        text("""
            SELECT source_doc, chunk_text,
                   1 - (embedding <=> :query_embedding) AS relevance
            FROM regulation_embeddings
            ORDER BY embedding <=> :query_embedding
            LIMIT :top_k
        """),
        {"query_embedding": str(query_embedding), "top_k": top_k},
    )

    return [
        {
            "source_doc": row.source_doc,
            "chunk_text": row.chunk_text,
            "relevance": round(float(row.relevance), 3),
        }
        for row in result
    ]