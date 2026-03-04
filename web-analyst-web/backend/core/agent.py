import openai
import os
import json
from typing import List, Tuple
from core.schemas import ExtractionResult, SourceResult, CombinedResult, SourceContent
from core.rag import VectorStore

class AgentLog:
    def __init__(self):
        self.entries = []
    
    def add(self, message: str, detail: str = ""):
        self.entries.append({"message": message, "detail": detail})
    
    def get_log(self) -> str:
        return "\n".join([e["message"] if isinstance(e, dict) else e for e in self.entries])

class WebAnalystAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        # Unset ALL proxy environment variables that break OpenAI client
        for key in list(os.environ.keys()):
            if 'proxy' in key.lower():
                del os.environ[key]
        
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
        """Extract structured insights from a single source with attribution"""
        
        plan = self.plan(analysis_mode)
        
        context_text = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts[:5])])
        
        tone_instructions = {
            "formal": "Write in a professional, business-appropriate style. Use markdown formatting: **bold** for emphasis, bullet points with -, numbered lists, and clear structure.",
            "friendly": "Write for someone who has NEVER done content analysis before. Explain everything simply. Use everyday language. No technical terms. Make it clear and easy to understand!"
        }
        
        prompt = f"""You are analyzing content for: {analysis_mode}

Source: {source.title}
Type: {source.type}
URL: {source.url}

Extraction Plan: {plan}

Retrieved Context (templates and style guides):
{context_text}

Content to analyze:
{source.content[:4000]}

IMPORTANT: Write in your own words. Do NOT copy-paste from the article. Synthesize and paraphrase the information naturally.

Tone: {tone_instructions.get(tone, tone_instructions["formal"])}
Output language: {language}

Extract structured insights in JSON format:
{{
  "summary": "Natural summary in 2-3 sentences{' using simple everyday language' if tone == 'friendly' else ''}",
  "key_points": ["Key point 1{' in simple language' if tone == 'friendly' else ''}", "Key point 2"],
  "recommendations_or_decisions": ["Recommendation 1{' in simple language' if tone == 'friendly' else ''}", "Recommendation 2"],
  "open_questions": ["Question 1{' in simple language' if tone == 'friendly' else ''}", "Question 2"],
  "risks_or_ambiguities": ["Risk or ambiguity 1{' in simple language' if tone == 'friendly' else ''}", "Risk 2"]
}}

{f'IMPORTANT: Use simple everyday language. Emojis are OPTIONAL - use sparingly at the START if helpful: "📌 This is important" NOT "This is important 📌"' if tone == 'friendly' else ''}

Rules:
- Write everything in natural, human language
- Use markdown formatting: **bold** for emphasis, - for bullets, clear structure
- Match the {tone} tone throughout
- {'Add relevant emojis throughout to make it engaging and visual' if tone == 'friendly' else 'Use professional formatting'}
- Be specific and actionable
- Set confidence lower if item is inferred or vague"""

        self.log.add("Sending request to AI model...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        self.log.add("Parsing AI response...")
        result_json = json.loads(response.choices[0].message.content)
        
        return SourceResult(
            url=source.url,
            title=source.title,
            type=source.type,
            summary=result_json.get("summary", ""),
            key_points=result_json.get("key_points", []),
            recommendations_or_decisions=result_json.get("recommendations_or_decisions", []),
            open_questions=result_json.get("open_questions", []),
            risks_or_ambiguities=result_json.get("risks_or_ambiguities", [])
        )
    
    def reflect_and_fix(
        self,
        source_result: SourceResult,
        source: SourceContent,
        analysis_mode: str
    ) -> Tuple[SourceResult, bool]:
        """Self-evaluate and fix extraction if needed"""
        
        self.log.add("Reviewing extraction quality...")
        issues = []
        
        # Check for missing content
        if len(source_result.key_points) < 2:
            issues.append("Too few key points extracted")
        
        if not issues:
            self.log.add(f"✓ Quality check passed")
            return source_result, False
        
        self.log.add(f"⚠ Found issues: {', '.join(issues)}")
        self.log.add("Re-analyzing to improve quality...")
        
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
        
        tone_instructions = {
            "formal": "Write in a professional style using markdown: **bold** for emphasis, bullet points with -, numbered lists, and clear structure.",
            "friendly": "Write for someone who has NEVER done content analysis before. Use simple everyday language. No technical terms or jargon. Make it clear and easy!"
        }
        
        prompt = f"""Combine insights from multiple sources into a cohesive analysis.

Source Summaries:
{all_summaries}

IMPORTANT: Write in natural, human language. Synthesize information in your own words.

Tone: {tone_instructions.get(tone, tone_instructions["formal"])}
Language: {language}

Generate a combined analysis in JSON. IMPORTANT: All fields must be arrays/lists:
{{
  "overall_summary": "Overall summary in 3-4 sentences{' using simple everyday language' if tone == 'friendly' else ''}",
  "cross_source_agreements": ["Agreement 1{' in simple language' if tone == 'friendly' else ''}", "Agreement 2"],
  "cross_source_conflicts": ["Conflict 1{' in simple language' if tone == 'friendly' else ''}", "Conflict 2"],
  "final_action_plan": ["Action 1{' in simple language' if tone == 'friendly' else ''}", "Action 2"],
  "confidence_notes": ["Note 1{' in simple language' if tone == 'friendly' else ''}", "Note 2"]
}}

CRITICAL: confidence_notes MUST be an array of strings, not a single string.
{f'IMPORTANT: Use everyday language! Emojis are OPTIONAL - use sparingly. If used, place at START: "✅ This works" NOT "This works ✅"' if tone == 'friendly' else ''}
Write everything using markdown formatting: **bold** for emphasis, - for bullets, clear structure."""

        self.log.add("Synthesizing insights from all sources...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result_json = json.loads(response.choices[0].message.content)
        
        # Fix type mismatches
        if isinstance(result_json.get('overall_summary'), list):
            result_json['overall_summary'] = ' '.join(result_json['overall_summary'])
        if isinstance(result_json.get('confidence_notes'), str):
            result_json['confidence_notes'] = [result_json['confidence_notes']]
        if isinstance(result_json.get('cross_source_agreements'), str):
            result_json['cross_source_agreements'] = [result_json['cross_source_agreements']]
        if isinstance(result_json.get('cross_source_conflicts'), str):
            result_json['cross_source_conflicts'] = [result_json['cross_source_conflicts']]
        if isinstance(result_json.get('final_action_plan'), str):
            result_json['final_action_plan'] = [result_json['final_action_plan']]
        
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
        
        # Adjust explanations based on tone
        if tone == "friendly":
            details = {
                "plan": "Starting up! I'm going to read the websites you gave me and find the important stuff. Like reading a book and taking notes! 📚",
                "processing": "I see all your links! I'll go through each one and see what's there.",
                "vector_store": "Now I'm organizing everything I read. Think of it like making a filing system - so I can quickly find any information later without reading everything again!",
                "indexed": "Perfect! Everything is organized now. I can search through it super fast! ✨",
                "skipped": "Couldn't open this page - maybe it's broken or blocked. No worries, I'll use the others!",
                "processing_source": "Reading this page now! I'm looking for key information, important points, and things you might need to do.",
                "retrieved": "Searching through my organized notes to find the most relevant information for this page!",
                "extracting": "Pulling out the important parts - the main ideas, key points, and action items you should know about!",
                "reflecting": "Double-checking my work to make sure I got everything right and didn't miss anything important!",
                "combining": "Now I'm putting together all the information from different pages into one clear summary for you!",
                "complete": "All finished! I've read everything, found the important parts, and organized it all for you! 🎉"
            }
        else:
            details = {
                "plan": "Initializing analysis strategy and preparing to process your content based on the selected mode.",
                "processing": "Loading and preparing all source URLs for analysis. Each will be analyzed individually before combining insights.",
                "vector_store": "Creating a searchable knowledge base from your content. Text is split into chunks and converted into vectors for semantic search.",
                "indexed": "Successfully created the knowledge base. Each chunk represents a searchable piece of content.",
                "skipped": "This source was skipped due to an error during content extraction.",
                "processing_source": "Deeply analyzing this source to extract key insights, identify action items, and gather relevant information.",
                "retrieved": "Using semantic search to find the most relevant pieces of content from the knowledge base for accurate citations.",
                "extracting": "Processing the content to identify key points, action items, and important information in a structured format.",
                "reflecting": "Self-reflection: Reviewing the work to check for accuracy, completeness, and quality. May refine findings based on this review.",
                "combining": "Merging insights from all sources into a comprehensive report. Identifying patterns, removing duplicates, and creating a unified view.",
                "complete": "Analysis finished! View the results, action items, and generated email draft in their respective tabs."
            }
        
        self.log.add(f"=== PLAN: {analysis_mode} ===", details["plan"])
        self.log.add(f"Processing {len(sources)} sources", details["processing"])
        
        # Build vector store
        self.log.add("=== BUILDING VECTOR STORE ===", details["vector_store"])
        from core.rag import build_vector_store
        self.vector_store = build_vector_store(sources, kb_docs)
        self.log.add(f"Indexed {self.vector_store.index.ntotal if self.vector_store.index else 0} chunks", details["indexed"])
        
        source_results = []
        
        for source in sources:
            if not source.content:
                self.log.add(f"✗ Skipping {source.url} (no content)", details["skipped"])
                continue
            
            self.log.add(f"=== PROCESSING: {source.title} ===", details["processing_source"])
            
            # Retrieve contexts
            query = f"{analysis_mode} analysis of {source.title}"
            contexts_raw = self.vector_store.retrieve(query, top_k=5)
            contexts = [text for text, meta, dist in contexts_raw]
            self.log.add(f"Retrieved {len(contexts)} contexts", details["retrieved"])
            
            # Extract
            self.log.add("Extracting structured insights...", details["extracting"])
            result = self.extract_structured_insights(source, contexts, analysis_mode, tone, language)
            
            # Reflect
            self.log.add("Reflecting on extraction quality...", details["reflecting"])
            result, was_fixed = self.reflect_and_fix(result, source, analysis_mode)
            
            source_results.append(result)
        
        # Combine
        self.log.add("=== COMBINING SOURCES ===", details["combining"])
        combined = self.combine_sources(source_results, tone, language)
        
        self.log.add("=== COMPLETE ===", details["complete"])
        
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
