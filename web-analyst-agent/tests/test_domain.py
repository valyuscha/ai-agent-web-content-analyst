import pytest
from core.domain import AnalysisPlanner, QualityReflector
from schemas import SourceResult, ActionItem
from config import AppConfig

def test_analysis_planner():
    assert "key concepts" in AnalysisPlanner.get_plan("Study notes")
    assert "value propositions" in AnalysisPlanner.get_plan("Product/marketing analysis")
    assert "main ideas" in AnalysisPlanner.get_plan("Unknown mode")

def test_quality_reflector_passes():
    config = AppConfig()
    reflector = QualityReflector(config)
    
    result = SourceResult(
        url="test",
        title="Test",
        type="article",
        summary="Test summary",
        key_points=["Point 1", "Point 2", "Point 3"],
        action_items=[
            ActionItem(task="Complete the detailed analysis report", confidence=0.8, source_quote="analysis report")
        ]
    )
    
    issues, passed = reflector.evaluate(result)
    assert passed
    assert len(issues) == 0

def test_quality_reflector_fails_few_points():
    config = AppConfig()
    reflector = QualityReflector(config)
    
    result = SourceResult(
        url="test",
        title="Test",
        type="article",
        summary="Test",
        key_points=["Only one"],
        action_items=[]
    )
    
    issues, passed = reflector.evaluate(result)
    assert not passed
    assert "Too few key points" in issues[0]

def test_quality_reflector_fails_low_confidence():
    config = AppConfig()
    reflector = QualityReflector(config)
    
    result = SourceResult(
        url="test",
        title="Test",
        type="article",
        summary="Test",
        key_points=["P1", "P2", "P3"],
        action_items=[
            ActionItem(task="Do something", confidence=0.3, source_quote=""),
            ActionItem(task="Do another", confidence=0.2, source_quote="")
        ]
    )
    
    issues, passed = reflector.evaluate(result)
    assert not passed
    assert any("low confidence" in issue.lower() for issue in issues)
