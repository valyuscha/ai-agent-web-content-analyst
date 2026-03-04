"""
Integration tests for complete RAG pipeline with attribution.
Addresses mentor feedback: "Consider adding more comprehensive unit tests"
"""
import pytest
from src.domain.chunking.sentence_chunker import chunk_text
from src.domain.attribution.attribution_utils import (
    format_chunks_for_llm,
    process_attribution
)


class TestRAGPipelineIntegration:
    """Test complete RAG pipeline: chunking → retrieval → attribution"""
    
    def test_single_source_pipeline(self):
        """Test pipeline with single source"""
        # 1. Chunk source
        text = "Quantum computing uses qubits. These enable superposition."
        chunks = chunk_text(
            text,
            "source-1",
            "https://quantum.com",
            "Quantum Guide"
        )
        
        assert len(chunks) >= 1
        assert all(c.metadata.source_id == "source-1" for c in chunks)
        
        # 2. Convert to dict format for LLM
        chunk_dicts = [
            {
                'text': c.text,
                'metadata': {
                    'source_id': c.metadata.source_id,
                    'chunk_index': c.metadata.chunk_index,
                    'url': c.metadata.url,
                    'title': c.metadata.title
                }
            }
            for c in chunks
        ]
        
        # 3. Format for LLM
        context = format_chunks_for_llm(chunk_dicts)
        assert '[S1:C0]' in context
        assert 'qubits' in context
        
        # 4. Simulate LLM response with citations
        llm_response = "Quantum computing uses qubits [S1:C0]."
        
        # 5. Process attribution
        attributed_text, citations = process_attribution(llm_response, chunk_dicts)
        
        # 6. Verify output
        assert '[1]' in attributed_text
        assert 'Sources:' in attributed_text
        assert 'Quantum Guide' in attributed_text
        assert len(citations) == 1
    
    def test_multiple_sources_pipeline(self):
        """Test pipeline with multiple sources"""
        # 1. Chunk multiple sources
        source1_chunks = chunk_text(
            "Quantum computing is revolutionary.",
            "source-1",
            "https://quantum.com",
            "Quantum Basics"
        )
        
        source2_chunks = chunk_text(
            "Machine learning enables AI.",
            "source-2",
            "https://ml.com",
            "ML Guide"
        )
        
        # 2. Combine chunks
        all_chunks = []
        for c in source1_chunks:
            all_chunks.append({
                'text': c.text,
                'metadata': {
                    'source_id': c.metadata.source_id,
                    'chunk_index': c.metadata.chunk_index,
                    'url': c.metadata.url,
                    'title': c.metadata.title
                }
            })
        
        for c in source2_chunks:
            all_chunks.append({
                'text': c.text,
                'metadata': {
                    'source_id': c.metadata.source_id,
                    'chunk_index': c.metadata.chunk_index,
                    'url': c.metadata.url,
                    'title': c.metadata.title
                }
            })
        
        # 3. Format for LLM
        context = format_chunks_for_llm(all_chunks)
        assert '[S1:C0]' in context
        assert '[S2:C0]' in context
        
        # 4. Simulate LLM response
        llm_response = "Quantum is revolutionary [S1:C0]. ML enables AI [S2:C0]."
        
        # 5. Process attribution
        attributed_text, citations = process_attribution(llm_response, all_chunks)
        
        # 6. Verify output
        assert '[1]' in attributed_text
        assert '[2]' in attributed_text
        assert len(citations) == 2
        assert citations[0].title == "Quantum Basics"
        assert citations[1].title == "ML Guide"
    
    def test_long_document_chunking_and_attribution(self):
        """Test with realistic long document"""
        long_text = """
        Quantum computing represents a paradigm shift in computation. Unlike classical computers
        that use bits, quantum computers use quantum bits or qubits. These qubits can exist
        in superposition, allowing them to represent multiple states simultaneously.
        
        The power of quantum computing comes from quantum entanglement. When qubits become
        entangled, the state of one qubit is dependent on the state of another, no matter
        the distance between them. This property enables quantum computers to solve certain
        problems exponentially faster than classical computers.
        
        Key algorithms include Shor's algorithm for factoring large numbers and Grover's
        algorithm for searching unsorted databases. These algorithms demonstrate the potential
        of quantum computing for cryptography and optimization problems.
        """
        
        # 1. Chunk with reasonable size
        chunks = chunk_text(
            long_text.strip(),
            "article-1",
            "https://quantum-article.com",
            "Quantum Computing Deep Dive",
            max_chars=300
        )
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # All chunks should have metadata
        for chunk in chunks:
            assert chunk.metadata.source_id == "article-1"
            assert chunk.metadata.title == "Quantum Computing Deep Dive"
        
        # 2. Convert to dict format
        chunk_dicts = [
            {
                'text': c.text,
                'metadata': {
                    'source_id': c.metadata.source_id,
                    'chunk_index': c.metadata.chunk_index,
                    'url': c.metadata.url,
                    'title': c.metadata.title
                }
            }
            for c in chunks
        ]
        
        # 3. Simulate using multiple chunks in response
        llm_response = f"Quantum computing uses qubits [S1:C0]. Entanglement is key [S1:C1]."
        
        # 4. Process attribution
        attributed_text, citations = process_attribution(llm_response, chunk_dicts)
        
        # 5. Should deduplicate to single source
        assert len(citations) == 1
        assert citations[0].title == "Quantum Computing Deep Dive"
    
    def test_chunk_overlap_preservation(self):
        """Test that chunk overlap is preserved and accessible"""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        
        chunks = chunk_text(
            text,
            "source-1",
            "url",
            "title",
            max_chars=50,
            overlap_sentences=1
        )
        
        if len(chunks) >= 2:
            # Verify chunks have content
            assert len(chunks[0].text) > 0
            assert len(chunks[1].text) > 0
            
            # Verify metadata is preserved
            assert chunks[0].metadata.chunk_index == 0
            assert chunks[1].metadata.chunk_index == 1
    
    def test_citation_only_for_used_chunks(self):
        """Test that only cited chunks appear in sources"""
        # Create 3 chunks
        chunks = [
            {
                'text': 'Chunk 1',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 0,
                    'title': 'Title 1',
                    'url': 'url1'
                }
            },
            {
                'text': 'Chunk 2',
                'metadata': {
                    'source_id': 'source-2',
                    'chunk_index': 0,
                    'title': 'Title 2',
                    'url': 'url2'
                }
            },
            {
                'text': 'Chunk 3',
                'metadata': {
                    'source_id': 'source-3',
                    'chunk_index': 0,
                    'title': 'Title 3',
                    'url': 'url3'
                }
            }
        ]
        
        # Only cite first two
        llm_response = "First [S1:C0] and second [S2:C0]."
        
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        # Should only have 2 citations
        assert len(citations) == 2
        assert 'Title 3' not in attributed_text


class TestChunkingAttributionEdgeCases:
    """Test edge cases in the pipeline"""
    
    def test_empty_text(self):
        chunks = chunk_text("", "source-1")
        assert chunks == []
    
    def test_very_short_text(self):
        chunks = chunk_text("Hi", "source-1", "url", "title")
        assert len(chunks) == 1
        assert chunks[0].text == "Hi"
    
    def test_no_citations_in_response(self):
        chunks = [{
            'text': 'Content',
            'metadata': {
                'source_id': 'source-1',
                'chunk_index': 0,
                'title': 'Title',
                'url': 'url'
            }
        }]
        
        llm_response = "Response without citations."
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        assert attributed_text == "Response without citations."
        assert len(citations) == 0
    
    def test_malformed_citation_ids(self):
        chunks = [{
            'text': 'Content',
            'metadata': {
                'source_id': 'source-1',
                'chunk_index': 0,
                'title': 'Title',
                'url': 'url'
            }
        }]
        
        # Malformed IDs should be left as-is
        llm_response = "Text [S1] and [C0] and [invalid]."
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        # Should not crash, malformed IDs left unchanged
        assert '[S1]' in attributed_text
        assert '[C0]' in attributed_text
