from typing import List, Tuple
from schemas import SourceContent, SourceResult, ExtractionResult, CombinedResult, ActionItem
from core.interfaces import VectorStoreInterface, LLMProvider
import json

class AnalysisPlanner:
    PLANS = {
        "Study notes": "Extract key concepts, definitions, examples, and learning objectives",
        "Product/marketing analysis": "Extract value propositions, target audience, pricing, competitive advantages, and market positioning",
        "Technical tutorial extraction": "Extract setup steps, code examples, prerequisites, troubleshooting tips, and best practices",
        "General summary": "Extract main ideas, supporting arguments, conclusions, and practical implications"
    }
    
    @staticmethod
    def get_plan(mode: str) -> str:
        return AnalysisPlanner.PLANS.get(mode, AnalysisPlanner.PLANS["General summary"])

class InsightExtractor:
    def __init__(self, llm: LLMProvider, config):
        self.llm = llm
        self.config = config
    
    def extract(
        self,
        source: SourceContent,
        contexts: List[str],
        analysis_mode: str,
        tone: str,
        language: str
    ) -> SourceResult:
        plan = AnalysisPlanner.get_plan(analysis_mode)
        context_text = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts[:5])])
        
        prompt = f"""You are analyzing content for: {analysis_mode}

Source: {source.title}
Type: {source.type}
URL: {source.url}

Extraction Plan: {plan}

Retrieved Context (templates and style guides):
{context_text}

Content to analyze:
{source.content[:4000]}

Extract structured insights in JSON format matching this schema:
{{
  "summary": "brief summary",
  "key_points": ["point1", "point2"],
  "recommendations_or_decisions": ["rec1"],
  "open_questions": ["question1"],
  "action_items": [
    {{
      "task": "specific actionable task",
      "owner": "TBD or extracted name",
      "due_date": "TBD or extracted date",
      "priority": "low|medium|high",
      "confidence": 0.0-1.0,
      "source_quote": "exact quote max 25 words"
    }}
  ],
  "risks_or_ambiguities": ["risk1"]
}}

Tone: {tone}
Output language: {language}

Rules:
- Action items must be specific and actionable
- Include source_quote for each action item (max 25 words from content)
- Set confidence lower if item is inferred or vague
- Be concise and practical"""

        result_json = json.loads(self.llm.generate(prompt, self.config.temperature, json_mode=True))
        action_items = [ActionItem(**item) for item in result_json.get("action_items", [])]
        
        return SourceResult(
            url=source.url,
            title=source.title,
            type=source.type,
            summary=result_json.get("summary", ""),
            key_points=result_json.get("key_points", []),
            recommendations_or_decisions=result_json.get("recommendations_or_decisions", []),
            open_questions=result_json.get("open_questions", []),
            action_items=action_items,
            risks_or_ambiguities=result_json.get("risks_or_ambiguities", [])
        )

class QualityReflector:
    def __init__(self, config):
        self.config = config
    
    def evaluate(self, result: SourceResult) -> Tuple[List[str], bool]:
        issues = []
        
        if len(result.key_points) < 2:
            issues.append("Too few key points extracted")
        
        low_conf_items = [item for item in result.action_items if item.confidence < 0.5]
        if len(low_conf_items) > len(result.action_items) * 0.5:
            issues.append("Too many low confidence action items")
        
        vague_items = [item for item in result.action_items if len(item.task.split()) < 4]
        if vague_items:
            issues.append("Vague action items detected")
        
        return issues, len(issues) == 0

class SourceCombiner:
    def __init__(self, llm: LLMProvider, config):
        self.llm = llm
        self.config = config
    
    def combine(
        self,
        source_results: List[SourceResult],
        tone: str,
        language: str
    ) -> CombinedResult:
        all_summaries = "\n\n".join([f"{sr.title}: {sr.summary}" for sr in source_results])
        all_actions = []
        for sr in source_results:
            for item in sr.action_items:
                all_actions.append(f"- {item.task} (from {sr.title})")
        
        prompt = f"""Combine insights from multiple sources:

{all_summaries}

All action items:
{chr(10).join(all_actions[:20])}

Generate a combined analysis in JSON:
{{
  "overall_summary": "synthesis of all sources",
  "cross_source_agreements": ["agreement1"],
  "cross_source_conflicts": ["conflict1"],
  "final_action_plan": ["prioritized action1"],
  "confidence_notes": ["note about reliability"]
}}

Tone: {tone}
Language: {language}"""

        result_json = json.loads(self.llm.generate(prompt, self.config.temperature, json_mode=True))
        return CombinedResult(**result_json)
