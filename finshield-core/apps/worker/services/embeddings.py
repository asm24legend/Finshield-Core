import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "api"))

import ollama
from pathlib import Path
from db import SessionLocal
from models.regulation_embedding import RegulationEmbedding

REGULATIONS_DIR = Path(__file__).resolve().parent.parent / "data" / "regulations"
CHUNK_SIZE_WORDS = 200   # roughly 250-300 tokens per chunk — small enough to be a
                          # focused, citable passage rather than a whole document
CHUNK_OVERLAP_WORDS = 30  # slight overlap so a concept split across chunks isn't lost


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP_WORDS) -> list[str]:
    """
    Splits text into overlapping word-count chunks. Overlap matters because
    a naive hard split can cut a sentence (and its meaning) exactly in half —
    the overlap gives each chunk a bit of surrounding context.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def embed_text(text: str) -> list[float]:
    """Generates a 768-dimension embedding vector using Ollama's local embedding model."""
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]


def ingest_regulations():
    db = SessionLocal()
    try:
        print("Clearing existing regulation_embeddings...")
        db.query(RegulationEmbedding).delete()
        db.commit()

        txt_files = list(REGULATIONS_DIR.glob("*.txt"))
        if not txt_files:
            print(f"No .txt files found in {REGULATIONS_DIR}")
            return

        total_chunks = 0
        for file_path in txt_files:
            source_name = file_path.stem  # filename without extension
            print(f"Processing {file_path.name}...")

            text = file_path.read_text(encoding="utf-8")
            chunks = chunk_text(text)
            print(f"  Split into {len(chunks)} chunks.")

            for i, chunk in enumerate(chunks):
                embedding = embed_text(chunk)
                entry = RegulationEmbedding(
                    source_doc=source_name,
                    chunk_text=chunk,
                    embedding=embedding,
                    doc_metadata={"chunk_index": i},
                )
                db.add(entry)
                total_chunks += 1

            db.commit()

        print(f"Done. {total_chunks} chunks embedded and stored.")
    finally:
        db.close()


if __name__ == "__main__":
    ingest_regulations()