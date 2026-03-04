import openai
import os
import json
from typing import List, Tuple
from schemas import ExtractionResult, SourceResult, CombinedResult, SourceContent, ActionItem
from rag import VectorStore

class AgentLog:
    def __init__(self):
        self.entries = []
    
    def add(self, message: str):
        self.entries.append(message)
    
    def get_log(self) -> str:
        return "\n".join(self.entries)

class WebAnalystAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.log = AgentLog()
        self.vector_store = None
    
    def plan(self, analysis_mode: str) -> str:
        """Generate extraction plan based on analysis mode"""
        plans = {
            "Study notes": "Extract key concepts, definitions, examples, and learning objectives",
            "Product/marketing analysis": "Extract value propositions, target audience, pricing, competitive advantages, and market positioning",
            "Technical tutorial extraction": "Extract setup steps, code examples, prerequisites, troubleshooting tips, and best practices",
            "General summary": "Extract main ideas, supporting arguments, conclusions, and practical implications"
        }
        return plans.get(analysis_mode, plans["General summary"])
    
    def extract_structured_insights(
        self, 
        source: SourceContent, 
        contexts: List[str],
        analysis_mode: str,
        tone: str,
        language: str
    ) -> SourceResult:
        """Extract structured insights from a single source"""
        
        plan = self.plan(analysis_mode)
        
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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result_json = json.loads(response.choices[0].message.content)
        
        # Convert to SourceResult
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
    
    def reflect_and_fix(
        self,
        source_result: SourceResult,
        source: SourceContent,
        analysis_mode: str
    ) -> Tuple[SourceResult, bool]:
        """Self-evaluate and fix extraction if needed"""
        
        issues = []
        
        # Check for missing content
        if len(source_result.key_points) < 2:
            issues.append("Too few key points extracted")
        
        # Check action items quality
        low_conf_items = [item for item in source_result.action_items if item.confidence < 0.5]
        if len(low_conf_items) > len(source_result.action_items) * 0.5:
            issues.append("Too many low confidence action items")
        
        vague_items = [item for item in source_result.action_items if len(item.task.split()) < 4]
        if vague_items:
            issues.append("Vague action items detected")
        
        if not issues:
            self.log.add(f"✓ Reflection passed for {source.title}")
            return source_result, False
        
        self.log.add(f"⚠ Reflection found issues for {source.title}: {', '.join(issues)}")
        
        # Re-retrieve with targeted queries
        queries = [
            f"action items and next steps in {source.title}",
            f"key takeaways from {source.title}",
            f"recommendations and decisions"
        ]
        
        contexts = []
        for query in queries:
            results = self.vector_store.retrieve(query, top_k=3)
            contexts.extend([text for text, meta, dist in results if meta.get("url") == source.url])
        
        self.log.add(f"↻ Re-extracting with {len(contexts)} targeted contexts")
        
        # Re-extract
        improved = self.extract_structured_insights(source, contexts, analysis_mode, "formal", "English")
        
        return improved, True
    
    def combine_sources(
        self,
        source_results: List[SourceResult],
        tone: str,
        language: str
    ) -> CombinedResult:
        """Combine insights from multiple sources"""
        
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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result_json = json.loads(response.choices[0].message.content)
        return CombinedResult(**result_json)
    
    def run(
        self,
        sources: List[SourceContent],
        kb_docs: List[Tuple[str, str]],
        analysis_mode: str,
        tone: str,
        language: str
    ) -> ExtractionResult:
        """Main agent loop"""
        
        self.log.add(f"=== PLAN: {analysis_mode} ===")
        self.log.add(f"Processing {len(sources)} sources")
        
        # Build vector store
        self.log.add("=== BUILDING VECTOR STORE ===")
        from rag import build_vector_store
        self.vector_store = build_vector_store(sources, kb_docs)
        self.log.add(f"Indexed {self.vector_store.index.ntotal if self.vector_store.index else 0} chunks")
        
        source_results = []
        
        for source in sources:
            if not source.content:
                self.log.add(f"✗ Skipping {source.url} (no content)")
                continue
            
            self.log.add(f"=== PROCESSING: {source.title} ===")
            
            # Retrieve contexts
            query = f"{analysis_mode} analysis of {source.title}"
            contexts_raw = self.vector_store.retrieve(query, top_k=5)
            contexts = [text for text, meta, dist in contexts_raw]
            self.log.add(f"Retrieved {len(contexts)} contexts")
            
            # Extract
            self.log.add("Extracting structured insights...")
            result = self.extract_structured_insights(source, contexts, analysis_mode, tone, language)
            
            # Reflect
            self.log.add("Reflecting on extraction quality...")
            result, was_fixed = self.reflect_and_fix(result, source, analysis_mode)
            
            source_results.append(result)
        
        # Combine
        self.log.add("=== COMBINING SOURCES ===")
        combined = self.combine_sources(source_results, tone, language)
        
        self.log.add("=== COMPLETE ===")
        
        return ExtractionResult(sources=source_results, combined=combined)
    
    def generate_email_draft(self, extraction: ExtractionResult, tone: str) -> str:
        """Generate follow-up email draft"""
        
        summary = extraction.combined.overall_summary
        actions = extraction.combined.final_action_plan[:5]
        
        prompt = f"""Generate a professional follow-up email summarizing these findings:

Summary: {summary}

Key Actions:
{chr(10).join([f"- {a}" for a in actions])}

Tone: {tone}
Keep it concise (max 200 words)."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        return response.choices[0].message.content
