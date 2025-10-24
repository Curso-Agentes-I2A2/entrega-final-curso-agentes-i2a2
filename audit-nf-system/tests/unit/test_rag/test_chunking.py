import pytest

def test_chunk_text_basic():
    from backend.rag.chunking import chunk_text
    text = " ".join([f"word{i}" for i in range(100)])
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert isinstance(chunks, list)
    assert len(chunks) > 1
