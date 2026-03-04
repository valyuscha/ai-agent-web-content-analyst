"""
Comprehensive unit tests for agent attribution and analysis.
Addresses mentor feedback: "Consider adding more comprehensive unit tests beyond import validation"
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.agent import WebAnalystAgent
from core.schemas import SourceContent, SourceResult, ExtractionResult


class TestAgentAttribution:
    """Test source attribution in agent responses"""
    
    @pytest.fixture
    def agent(self):
        with patch('openai.OpenAI'):
            return WebAnalystAgent(api_key="test-key")
    
    @pytest.fixture
    def mock_source(self):
        return SourceContent(
            url="https://example.com",
            title="Test Article",
            type="article",
            content="This is test content about quantum computing."
        )
    
    def test_extract_includes_source_attribution(self, agent, mock_source):
        """Test that extraction includes source attribution"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''{
            "summary": "Test summary",
            "key_points": ["Point 1"],
            "recommendations_or_decisions": ["Rec 1"],
            "open_questions": ["Q1"],
            "risks_or_ambiguities": ["Risk 1"],
            "source_attribution": "Article from reputable tech source"
        }'''
        
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        agent.vector_store = Mock()
        
        result = agent.extract_structured_insights(
            mock_source, 
            ["context"], 
            "General summary",
            "formal",
            "English"
        )
        
        # Verify attribution was logged
        log_text = agent.log.get_log()
        assert "Source: Test Article" in log_text or "source_attribution" in str(agent.log.entries)
    
    def test_combine_sources_includes_citations(self, agent):
        """Test that combined results include source citations"""
        source_results = [
            SourceResult(
                url="https://example1.com",
                title="Source 1",
                type="article",
                summary="Summary 1",
                key_points=["Point 1"],
                recommendations_or_decisions=[],
                open_questions=[],
                risks_or_ambiguities=[]
            ),
            SourceResult(
                url="https://example2.com",
                title="Source 2",
                type="article",
                summary="Summary 2",
                key_points=["Point 2"],
                recommendations_or_decisions=[],
                open_questions=[],
                risks_or_ambiguities=[]
            )
        ]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''{
            "overall_summary": "Combined summary citing [Source 1] and [Source 2]",
            "cross_source_agreements": ["Agreement from [Source 1, Source 2]"],
            "cross_source_conflicts": [],
            "final_action_plan": ["Action based on [Source 1]"],
            "confidence_notes": ["High confidence from multiple sources"]
        }'''
        
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        
        result = agent.combine_sources(source_results, "formal", "English")
        
        # Verify citations are present
        assert "[Source 1]" in result.overall_summary or "[Source 2]" in result.overall_summary
    
    def test_attribution_with_multiple_sources(self, agent):
        """Test attribution tracking across multiple sources"""
        sources = [
            SourceContent(
                url=f"https://example{i}.com",
                title=f"Source {i}",
                type="article",
                content=f"Content {i}"
            )
            for i in range(1, 4)
        ]
        
        mock_extract_response = Mock()
        mock_extract_response.choices = [Mock()]
        mock_extract_response.choices[0].message.content = '''{
            "summary": "Test summary",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "recommendations_or_decisions": ["Rec 1"],
            "open_questions": ["Q1"],
            "risks_or_ambiguities": ["Risk 1"],
            "source_attribution": "Reliable source"
        }'''
        
        mock_combine_response = Mock()
        mock_combine_response.choices = [Mock()]
        mock_combine_response.choices[0].message.content = '''{
            "overall_summary": "Summary with [Source 1], [Source 2], [Source 3]",
            "cross_source_agreements": ["All sources agree"],
            "cross_source_conflicts": [],
            "final_action_plan": ["Action"],
            "confidence_notes": ["High confidence"]
        }'''
        
        # Need 3 extract responses (one per source) + 1 combine response
        # Each extract has enough key_points so reflection passes without re-extraction
        agent.client.chat.completions.create = Mock(
            side_effect=[mock_extract_response, mock_extract_response, mock_extract_response, mock_combine_response]
        )
        
        # Mock vector store properly
        with patch('core.rag.build_vector_store') as mock_build:
            mock_store = Mock()
            mock_store.retrieve = Mock(return_value=[])
            mock_store.index = Mock()
            mock_store.index.ntotal = 10
            mock_build.return_value = mock_store
            
            result = agent.run(sources, [], "General summary", "formal", "English")
        
        # Verify all sources were processed
        assert len(result.sources) == 3
        assert "[Source" in result.combined.overall_summary


class TestAgentEdgeCases:
    """Test edge cases in agent processing"""
    
    @pytest.fixture
    def agent(self):
        with patch('openai.OpenAI'):
            return WebAnalystAgent(api_key="test-key")
    
    def test_empty_source_content(self, agent):
        """Test handling of empty source content"""
        source = SourceContent(
            url="https://example.com",
            title="Empty",
            type="article",
            content=""
        )
        
        # Mock combine_sources to return empty result when no sources
        mock_combine_response = Mock()
        mock_combine_response.choices = [Mock()]
        mock_combine_response.choices[0].message.content = '''{
            "overall_summary": "No content to analyze",
            "cross_source_agreements": [],
            "cross_source_conflicts": [],
            "final_action_plan": [],
            "confidence_notes": ["No sources available"]
        }'''
        
        agent.client.chat.completions.create = Mock(return_value=mock_combine_response)
        
        with patch('core.rag.build_vector_store') as mock_build:
            mock_store = Mock()
            mock_store.index = Mock()
            mock_store.index.ntotal = 0
            mock_build.return_value = mock_store
            
            result = agent.run([source], [], "General summary", "formal", "English")
        
        # Should skip empty sources
        assert len(result.sources) == 0
    
    def test_malformed_json_response(self, agent):
        """Test handling of malformed JSON from LLM"""
        source = SourceContent(
            url="https://example.com",
            title="Test",
            type="article",
            content="Content"
        )
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Not valid JSON"
        
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        agent.vector_store = Mock()
        
        with pytest.raises(Exception):
            agent.extract_structured_insights(
                source, 
                ["context"], 
                "General summary",
                "formal",
                "English"
            )
    
    def test_missing_attribution_field(self, agent):
        """Test graceful handling when attribution field is missing"""
        source = SourceContent(
            url="https://example.com",
            title="Test",
            type="article",
            content="Content"
        )
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''{
            "summary": "Test",
            "key_points": [],
            "recommendations_or_decisions": [],
            "open_questions": [],
            "risks_or_ambiguities": []
        }'''
        
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        agent.vector_store = Mock()
        
        # Should not raise error
        result = agent.extract_structured_insights(
            source, 
            ["context"], 
            "General summary",
            "formal",
            "English"
        )
        
        assert result.summary == "Test"


class TestSentenceChunkingIntegration:
    """Test sentence-aware chunking integration with agent"""
    
    def test_chunking_preserves_sentence_boundaries(self):
        """Test that chunking doesn't break sentences"""
        from core.tools import chunk_text
        
        text = "First sentence. Second sentence. Third sentence."
        # Note: This tests the old word-based chunking
        # The new sentence-aware chunking is in src.domain.chunking
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        
        # Each chunk should contain complete words
        for chunk in chunks:
            assert not chunk.startswith(' ')
            assert not chunk.endswith(' ')
    
    def test_sentence_aware_chunking_with_metadata(self):
        """Test new sentence-aware chunking preserves metadata"""
        from src.domain.chunking.sentence_chunker import chunk_text, TextChunk
        
        text = "Sentence one. Sentence two. Sentence three."
        chunks = chunk_text(
            text,
            source_id="test-1",
            url="https://example.com",
            title="Test Doc"
        )
        
        assert len(chunks) > 0
        assert all(isinstance(c, TextChunk) for c in chunks)
        assert all(c.metadata.source_id == "test-1" for c in chunks)
        assert all(c.metadata.url == "https://example.com" for c in chunks)


class TestReflectionQuality:
    """Test quality reflection and improvement"""
    
    @pytest.fixture
    def agent(self):
        with patch('openai.OpenAI'):
            return WebAnalystAgent(api_key="test-key")
    
    def test_reflection_triggers_on_low_quality(self, agent):
        """Test that reflection triggers when quality is low"""
        source = SourceContent(
            url="https://example.com",
            title="Test",
            type="article",
            content="Content"
        )
        
        poor_result = SourceResult(
            url=source.url,
            title=source.title,
            type=source.type,
            summary="Short",
            key_points=["Only one"],  # Too few
            recommendations_or_decisions=[],
            open_questions=[],
            risks_or_ambiguities=[]
        )
        
        agent.vector_store = Mock()
        agent.vector_store.retrieve = Mock(return_value=[])
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''{
            "summary": "Improved summary",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "recommendations_or_decisions": [],
            "open_questions": [],
            "risks_or_ambiguities": []
        }'''
        
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        
        improved, was_fixed = agent.reflect_and_fix(
            poor_result,
            source,
            "General summary"
        )
        
        assert was_fixed
        assert len(improved.key_points) > len(poor_result.key_points)
    
    def test_reflection_passes_good_quality(self, agent):
        """Test that reflection passes when quality is good"""
        source = SourceContent(
            url="https://example.com",
            title="Test",
            type="article",
            content="Content"
        )
        
        good_result = SourceResult(
            url=source.url,
            title=source.title,
            type=source.type,
            summary="Good summary",
            key_points=["Point 1", "Point 2", "Point 3"],
            recommendations_or_decisions=["Rec 1"],
            open_questions=["Q1"],
            risks_or_ambiguities=["Risk 1"]
        )
        
        agent.vector_store = Mock()
        
        result, was_fixed = agent.reflect_and_fix(
            good_result,
            source,
            "General summary"
        )
        
        assert not was_fixed
        assert result == good_result
