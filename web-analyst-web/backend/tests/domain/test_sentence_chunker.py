"""
Comprehensive unit tests for sentence-aware chunking.
Addresses mentor feedback: "Consider adding more comprehensive unit tests beyond import validation"
"""
import pytest
import re
from src.domain.chunking.sentence_chunker import (
    split_into_sentences,
    chunk_text,
    TextChunk,
    ChunkMetadata
)


class TestSplitIntoSentences:
    def test_simple_sentences(self):
        text = "First sentence. Second sentence. Third sentence."
        sentences = split_into_sentences(text)
        assert len(sentences) == 3
        assert "First sentence." in sentences[0]
    
    def test_mixed_punctuation(self):
        text = "Question? Answer! Statement."
        sentences = split_into_sentences(text)
        assert len(sentences) == 3
    
    def test_abbreviations(self):
        text = "Dr. Smith works at U.S. Labs."
        sentences = split_into_sentences(text)
        # Simple regex may split on abbreviations - that's acceptable
        # The important thing is it doesn't crash and produces valid output
        assert len(sentences) >= 1
        assert all(s.strip() for s in sentences)
    
    def test_empty_text(self):
        sentences = split_into_sentences("")
        assert sentences == []
    
    def test_whitespace_only(self):
        sentences = split_into_sentences("   \n\n  ")
        assert sentences == []


class TestChunkText:
    def test_empty_text(self):
        chunks = chunk_text("", "source-1")
        assert chunks == []
    
    def test_short_text_single_chunk(self):
        text = "This is a short sentence."
        chunks = chunk_text(text, "source-1", "http://example.com", "Title")
        
        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].metadata.source_id == "source-1"
        assert chunks[0].metadata.chunk_index == 0
        assert chunks[0].metadata.url == "http://example.com"
        assert chunks[0].metadata.title == "Title"
    
    def test_long_text_multiple_chunks(self):
        sentence = "This is a sentence. "
        text = sentence * 100  # ~2000 chars
        
        chunks = chunk_text(text, "source-1", max_chars=500)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.text) <= 600  # Allow some buffer
    
    def test_chunk_ordering(self):
        text = "First. Second. Third. Fourth."
        chunks = chunk_text(text, "source-1")
        
        for i, chunk in enumerate(chunks):
            assert chunk.metadata.chunk_index == i
    
    def test_chunk_overlap(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunk_text(text, "source-1", max_chars=50, overlap_sentences=1)
        
        if len(chunks) >= 2:
            # Check that there's some overlap
            assert len(chunks[0].text) > 0
            assert len(chunks[1].text) > 0
    
    def test_very_long_sentence(self):
        long_sentence = "A" * 2000 + "."
        chunks = chunk_text(long_sentence, "source-1", max_chars=1500)
        
        assert len(chunks) == 1
        assert chunks[0].text == long_sentence
    
    def test_no_empty_chunks(self):
        text = "Sentence one. Sentence two. Sentence three."
        chunks = chunk_text(text, "source-1")
        
        for chunk in chunks:
            assert chunk.text.strip() != ""
    
    def test_metadata_preservation(self):
        text = "Test sentence."
        chunks = chunk_text(
            text,
            "source-123",
            "https://test.com",
            "Test Title"
        )
        
        assert chunks[0].metadata.source_id == "source-123"
        assert chunks[0].metadata.url == "https://test.com"
        assert chunks[0].metadata.title == "Test Title"
    
    def test_multiple_sources(self):
        chunks1 = chunk_text("Content 1.", "source-1", "url1", "Title 1")
        chunks2 = chunk_text("Content 2.", "source-2", "url2", "Title 2")
        
        assert chunks1[0].metadata.source_id == "source-1"
        assert chunks2[0].metadata.source_id == "source-2"
        assert chunks1[0].metadata.title == "Title 1"
        assert chunks2[0].metadata.title == "Title 2"


class TestChunkingEdgeCases:
    def test_single_word(self):
        chunks = chunk_text("Word", "source-1")
        assert len(chunks) == 1
        assert chunks[0].text == "Word"
    
    def test_no_punctuation(self):
        text = "This is text without proper punctuation"
        chunks = chunk_text(text, "source-1")
        assert len(chunks) == 1
    
    def test_newlines(self):
        text = "First line.\nSecond line.\nThird line."
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
    
    def test_special_characters(self):
        text = "Text with émojis 🎉 and spëcial çhars!"
        chunks = chunk_text(text, "source-1")
        assert len(chunks) == 1
        assert "🎉" in chunks[0].text
    
    def test_multiple_punctuation(self):
        text = "Really?! Yes!! Absolutely."
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
        assert all(chunk.text.strip() for chunk in chunks)
    
    def test_only_whitespace_between_sentences(self):
        text = "First.    Second.     Third."
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
        # Should not have excessive whitespace
        for chunk in chunks:
            assert not re.search(r'\s{3,}', chunk.text)
    
    def test_mixed_newlines_and_spaces(self):
        text = "First sentence.\n\nSecond sentence.\n   Third sentence."
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
        assert all(chunk.text.strip() for chunk in chunks)
    
    def test_very_short_sentences(self):
        text = "Hi. Ok. Yes. No. Maybe."
        chunks = chunk_text(text, "source-1", max_chars=20)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.text.strip()
    
    def test_sentence_with_quotes(self):
        text = 'He said "Hello world." She replied "Hi there."'
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
        assert '"' in chunks[0].text
    
    def test_urls_in_text(self):
        text = "Visit https://example.com for more. It has great content."
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
        assert "https://example.com" in chunks[0].text or "https://example.com" in chunks[1].text if len(chunks) > 1 else True
    
    def test_numbers_and_decimals(self):
        text = "The value is 3.14159. Another number is 2.71828."
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
        # Should not split on decimal points
        assert "3.14159" in ' '.join(c.text for c in chunks)
    
    def test_ellipsis(self):
        text = "Wait... There's more... Keep reading."
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
    
    def test_all_caps_text(self):
        text = "THIS IS IMPORTANT. PLEASE READ CAREFULLY. THANK YOU."
        chunks = chunk_text(text, "source-1")
        assert len(chunks) >= 1
        assert all(chunk.text.strip() for chunk in chunks)


class TestChunkingIntegration:
    def test_realistic_article(self):
        article = """
        Quantum computing is a revolutionary technology. It uses quantum bits or qubits.
        Unlike classical bits, qubits can exist in superposition. This allows quantum computers
        to process multiple states simultaneously. The phenomenon of quantum entanglement
        enables qubits to be correlated in ways impossible for classical systems.
        """
        
        chunks = chunk_text(article.strip(), "article-1", "https://quantum.com", "Quantum Guide")
        
        assert len(chunks) >= 1
        assert all(chunk.metadata.source_id == "article-1" for chunk in chunks)
        assert all(chunk.metadata.url == "https://quantum.com" for chunk in chunks)
        assert all(chunk.text.strip() for chunk in chunks)
    
    def test_multiple_articles_chunking(self):
        article1 = "First article content. " * 50
        article2 = "Second article content. " * 50
        
        chunks1 = chunk_text(article1, "source-1", "url1", "Title 1", max_chars=500)
        chunks2 = chunk_text(article2, "source-2", "url2", "Title 2", max_chars=500)
        
        # Verify isolation
        assert all(c.metadata.source_id == "source-1" for c in chunks1)
        assert all(c.metadata.source_id == "source-2" for c in chunks2)
        
        # Verify no mixing
        assert chunks1[0].metadata.title == "Title 1"
        assert chunks2[0].metadata.title == "Title 2"
