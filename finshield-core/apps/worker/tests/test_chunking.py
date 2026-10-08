from services.embeddings import chunk_text


def test_chunks_overlap_correctly():
    words = [f"w{i}" for i in range(500)]
    chunks = chunk_text(" ".join(words), chunk_size=200, overlap=30)
    assert len(chunks) == 3
    # last 30 words of chunk 0 are the first 30 words of chunk 1
    assert chunks[0].split()[-30:] == chunks[1].split()[:30]


def test_empty_text_gives_no_chunks():
    assert chunk_text("") == []