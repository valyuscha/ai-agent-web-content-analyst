import pytest
from infrastructure.text_processing import chunk_text

def test_chunk_text_basic():
    text = " ".join([f"word{i}" for i in range(100)])
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    
    assert len(chunks) > 1
    assert all(len(chunk.split()) <= 20 for chunk in chunks)

def test_chunk_text_short():
    text = "short text"
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_text_empty():
    chunks = chunk_text("", chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == ""

def test_chunk_text_overlap():
    text = " ".join([f"word{i}" for i in range(50)])
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    
    # Check overlap exists
    if len(chunks) > 1:
        first_words = chunks[0].split()[-5:]
        second_words = chunks[1].split()[:5]
        # Some overlap should exist
        assert len(set(first_words) & set(second_words)) > 0
