"""
Comprehensive unit tests for source attribution.
Addresses mentor feedback: "Consider adding more comprehensive unit tests beyond import validation"
"""
import pytest
from src.domain.attribution.attribution_utils import (
    format_chunk_id,
    format_chunks_for_llm,
    build_citation_map,
    process_attribution,
    Citation,
    ATTRIBUTION_SYSTEM_PROMPT
)


class TestFormatChunkId:
    def test_standard_format(self):
        assert format_chunk_id("source-1", 0) == "[S1:C0]"
        assert format_chunk_id("source-2", 3) == "[S2:C3]"
    
    def test_non_numeric_source_id(self):
        assert format_chunk_id("abc", 0) == "[S0:C0]"
        assert format_chunk_id("source", 1) == "[S0:C1]"
    
    def test_large_numbers(self):
        assert format_chunk_id("source-123", 99) == "[S123:C99]"


class TestFormatChunksForLLM:
    def test_single_chunk(self):
        chunks = [{
            'text': 'Test content.',
            'metadata': {
                'source_id': 'source-1',
                'chunk_index': 0
            }
        }]
        
        formatted = format_chunks_for_llm(chunks)
        assert '[S1:C0]' in formatted
        assert 'Test content.' in formatted
    
    def test_multiple_chunks(self):
        chunks = [
            {
                'text': 'First chunk.',
                'metadata': {'source_id': 'source-1', 'chunk_index': 0}
            },
            {
                'text': 'Second chunk.',
                'metadata': {'source_id': 'source-1', 'chunk_index': 1}
            }
        ]
        
        formatted = format_chunks_for_llm(chunks)
        assert '[S1:C0]' in formatted
        assert '[S1:C1]' in formatted
        assert 'First chunk.' in formatted
        assert 'Second chunk.' in formatted
    
    def test_empty_chunks(self):
        formatted = format_chunks_for_llm([])
        assert formatted == ""
    
    def test_missing_metadata(self):
        chunks = [{'text': 'Content', 'metadata': {}}]
        formatted = format_chunks_for_llm(chunks)
        assert '[S0:C0]' in formatted


class TestBuildCitationMap:
    def test_single_source(self):
        chunks = [{
            'text': 'Content',
            'metadata': {
                'source_id': 'source-1',
                'chunk_index': 0,
                'title': 'Title 1',
                'url': 'http://example.com'
            }
        }]
        
        citation_map = build_citation_map(chunks)
        citation = citation_map['[S1:C0]']
        
        assert citation.id == 1
        assert citation.title == 'Title 1'
        assert citation.url == 'http://example.com'
        assert citation.source_id == 'source-1'
    
    def test_multiple_sources(self):
        chunks = [
            {
                'text': 'Content 1',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 0,
                    'title': 'Title 1',
                    'url': 'url1'
                }
            },
            {
                'text': 'Content 2',
                'metadata': {
                    'source_id': 'source-2',
                    'chunk_index': 0,
                    'title': 'Title 2',
                    'url': 'url2'
                }
            }
        ]
        
        citation_map = build_citation_map(chunks)
        
        assert citation_map['[S1:C0]'].id == 1
        assert citation_map['[S2:C0]'].id == 2
        assert citation_map['[S1:C0]'].title == 'Title 1'
        assert citation_map['[S2:C0]'].title == 'Title 2'
    
    def test_same_source_multiple_chunks(self):
        chunks = [
            {
                'text': 'Chunk 1',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 0,
                    'title': 'Title',
                    'url': 'url'
                }
            },
            {
                'text': 'Chunk 2',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 1,
                    'title': 'Title',
                    'url': 'url'
                }
            }
        ]
        
        citation_map = build_citation_map(chunks)
        
        # Same source should have same citation ID
        assert citation_map['[S1:C0]'].id == citation_map['[S1:C1]'].id
    
    def test_missing_metadata(self):
        chunks = [{
            'text': 'Content',
            'metadata': {'source_id': 'source-1', 'chunk_index': 0}
        }]
        
        citation_map = build_citation_map(chunks)
        citation = citation_map['[S1:C0]']
        
        assert citation.title == 'Untitled'
        assert citation.url == ''


class TestProcessAttribution:
    def test_single_citation(self):
        chunks = [{
            'text': 'Content',
            'metadata': {
                'source_id': 'source-1',
                'chunk_index': 0,
                'title': 'Title 1',
                'url': 'http://example.com'
            }
        }]
        
        llm_response = "Statement [S1:C0]."
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        assert "[1]" in attributed_text
        assert "Sources:" in attributed_text
        assert "Title 1" in attributed_text
        assert len(citations) == 1
        assert citations[0].id == 1
    
    def test_multiple_citations(self):
        chunks = [
            {
                'text': 'Content 1',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 0,
                    'title': 'Title 1',
                    'url': 'url1'
                }
            },
            {
                'text': 'Content 2',
                'metadata': {
                    'source_id': 'source-2',
                    'chunk_index': 0,
                    'title': 'Title 2',
                    'url': 'url2'
                }
            }
        ]
        
        llm_response = "First [S1:C0] and second [S2:C0]."
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        assert "[1]" in attributed_text
        assert "[2]" in attributed_text
        assert len(citations) == 2
    
    def test_deduplication(self):
        chunks = [
            {
                'text': 'Chunk 1',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 0,
                    'title': 'Title',
                    'url': 'url'
                }
            },
            {
                'text': 'Chunk 2',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 1,
                    'title': 'Title',
                    'url': 'url'
                }
            }
        ]
        
        llm_response = "First [S1:C0] and second [S1:C1]."
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        # Both should map to [1], plus one in "Sources: [1]"
        assert attributed_text.count("[1]") == 3  # Two in text + one in sources
        assert len(citations) == 1  # Only one source
    
    def test_only_used_citations(self):
        chunks = [
            {
                'text': 'Content 1',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 0,
                    'title': 'Title 1',
                    'url': 'url1'
                }
            },
            {
                'text': 'Content 2',
                'metadata': {
                    'source_id': 'source-2',
                    'chunk_index': 0,
                    'title': 'Title 2',
                    'url': 'url2'
                }
            }
        ]
        
        llm_response = "Only first [S1:C0]."
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        assert len(citations) == 1
        assert citations[0].title == 'Title 1'
        assert 'Title 2' not in attributed_text
    
    def test_no_citations(self):
        chunks = [{
            'text': 'Content',
            'metadata': {
                'source_id': 'source-1',
                'chunk_index': 0,
                'title': 'Title',
                'url': 'url'
            }
        }]
        
        llm_response = "Statement without citations."
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        assert attributed_text == "Statement without citations."
        assert len(citations) == 0
    
    def test_citation_sorting(self):
        chunks = [
            {
                'text': 'Content 1',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 0,
                    'title': 'Title 1',
                    'url': 'url1'
                }
            },
            {
                'text': 'Content 2',
                'metadata': {
                    'source_id': 'source-2',
                    'chunk_index': 0,
                    'title': 'Title 2',
                    'url': 'url2'
                }
            }
        ]
        
        # Cite in reverse order
        llm_response = "Second [S2:C0] then first [S1:C0]."
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        # Citations should be sorted by ID
        assert citations[0].id == 1
        assert citations[1].id == 2


class TestAttributionSystemPrompt:
    def test_prompt_exists(self):
        assert ATTRIBUTION_SYSTEM_PROMPT
        assert 'cite' in ATTRIBUTION_SYSTEM_PROMPT.lower()
        assert '[S' in ATTRIBUTION_SYSTEM_PROMPT
        assert ':C' in ATTRIBUTION_SYSTEM_PROMPT


class TestAttributionIntegration:
    def test_complete_pipeline(self):
        """Test complete chunking → attribution pipeline"""
        chunks = [
            {
                'text': 'Quantum computing uses qubits.',
                'metadata': {
                    'source_id': 'source-1',
                    'chunk_index': 0,
                    'title': 'Quantum Guide',
                    'url': 'https://quantum.com'
                }
            },
            {
                'text': 'Machine learning enables AI.',
                'metadata': {
                    'source_id': 'source-2',
                    'chunk_index': 0,
                    'title': 'ML Guide',
                    'url': 'https://ml.com'
                }
            }
        ]
        
        # Format for LLM
        context = format_chunks_for_llm(chunks)
        assert '[S1:C0]' in context
        assert '[S2:C0]' in context
        
        # Simulate LLM response
        llm_response = "Quantum computing uses qubits [S1:C0]. ML enables AI [S2:C0]."
        
        # Process attribution
        attributed_text, citations = process_attribution(llm_response, chunks)
        
        # Verify output
        assert '[1]' in attributed_text
        assert '[2]' in attributed_text
        assert 'Sources:' in attributed_text
        assert 'Quantum Guide' in attributed_text
        assert 'ML Guide' in attributed_text
        assert len(citations) == 2
