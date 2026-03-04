"""
Source attribution utilities for RAG responses.
Addresses mentor feedback: "Could add source attribution in the final answer"
"""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Citation:
    """Citation information"""
    id: int
    title: str
    url: str
    source_id: str


def format_chunk_id(source_id: str, chunk_index: int) -> str:
    """Format chunk ID for LLM context: [S1:C0]"""
    source_num = ''.join(filter(str.isdigit, source_id)) or '0'
    return f"[S{source_num}:C{chunk_index}]"


def format_chunks_for_llm(chunks: List[Dict]) -> str:
    """
    Format chunks with IDs for LLM context.
    
    Args:
        chunks: List of dicts with 'text' and 'metadata' keys
        
    Returns:
        Formatted string with chunk IDs
    """
    formatted = []
    for chunk in chunks:
        metadata = chunk.get('metadata', {})
        chunk_id = format_chunk_id(
            metadata.get('source_id', '0'),
            metadata.get('chunk_index', 0)
        )
        formatted.append(f"{chunk_id} {chunk['text']}")
    
    return '\n\n'.join(formatted)


def build_citation_map(chunks: List[Dict]) -> Dict[str, Citation]:
    """Build mapping from chunk IDs to citations"""
    citation_map = {}
    source_map = {}
    
    for chunk in chunks:
        metadata = chunk.get('metadata', {})
        source_id = metadata.get('source_id', 'unknown')
        
        if source_id not in source_map:
            source_map[source_id] = {
                'id': len(source_map) + 1,
                'title': metadata.get('title', 'Untitled'),
                'url': metadata.get('url', '')
            }
        
        chunk_id = format_chunk_id(source_id, metadata.get('chunk_index', 0))
        citation_map[chunk_id] = Citation(
            id=source_map[source_id]['id'],
            title=source_map[source_id]['title'],
            url=source_map[source_id]['url'],
            source_id=source_id
        )
    
    return citation_map


def process_attribution(
    llm_response: str,
    chunks: List[Dict]
) -> Tuple[str, List[Citation]]:
    """
    Replace chunk IDs with citation numbers and build citation list.
    
    Args:
        llm_response: LLM response with chunk IDs like [S1:C0]
        chunks: List of chunks used in context
        
    Returns:
        Tuple of (attributed_text, used_citations)
    """
    citation_map = build_citation_map(chunks)
    used_citations = {}
    
    def replace_citation(match):
        chunk_id = match.group(0)
        if chunk_id in citation_map:
            citation = citation_map[chunk_id]
            used_citations[citation.source_id] = citation
            return f"[{citation.id}]"
        return chunk_id
    
    # Replace chunk IDs with citation numbers
    attributed_text = re.sub(r'\[S\d+:C\d+\]', replace_citation, llm_response)
    
    # Build citation list
    citations = sorted(used_citations.values(), key=lambda x: x.id)
    
    if citations:
        citation_list = '\n\nSources:\n' + '\n'.join(
            f"[{c.id}] {c.title}" + (f" — {c.url}" if c.url else "")
            for c in citations
        )
        attributed_text += citation_list
    
    return attributed_text, citations


ATTRIBUTION_SYSTEM_PROMPT = """
When providing your analysis, cite the sources by including the chunk ID in square brackets immediately after the relevant statement.

For example:
- "The research shows significant improvements [S1:C2]."
- "According to the study, the results were positive [S2:C0]."

Always cite the specific chunk that supports your statement. Use the exact chunk ID format provided in the context.
""".strip()
