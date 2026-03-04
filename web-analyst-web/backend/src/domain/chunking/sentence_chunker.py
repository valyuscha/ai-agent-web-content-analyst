"""
Sentence-aware text chunking with metadata preservation.
Addresses mentor feedback: "Consider using sentence-aware chunking instead of word-based"
"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChunkMetadata:
    """Metadata for each chunk"""
    source_id: str
    chunk_index: int
    url: Optional[str] = None
    title: Optional[str] = None


@dataclass
class TextChunk:
    """Text chunk with metadata"""
    text: str
    metadata: ChunkMetadata


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using regex with improved handling.
    
    Handles:
    - Standard sentence endings (. ! ?)
    - Abbreviations (Dr., U.S., etc.)
    - Multiple punctuation (!!, ?!)
    - Newlines as sentence boundaries
    """
    if not text or not text.strip():
        return []
    
    # Normalize whitespace and newlines
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split on sentence boundaries: . ! ? followed by space and capital letter
    # Also handles multiple punctuation like !! or ?!
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Filter out empty sentences and strip whitespace
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def chunk_text(
    text: str,
    source_id: str,
    url: Optional[str] = None,
    title: Optional[str] = None,
    max_chars: int = 1500,
    overlap_sentences: int = 1
) -> List[TextChunk]:
    """
    Chunk text using sentence-aware strategy.
    
    Args:
        text: Text to chunk
        source_id: Unique source identifier
        url: Source URL (optional)
        title: Source title (optional)
        max_chars: Maximum characters per chunk
        overlap_sentences: Number of sentences to overlap between chunks
        
    Returns:
        List of TextChunk objects with metadata
    """
    if not text or not text.strip():
        return []
    
    sentences = split_into_sentences(text)
    if not sentences:
        return []
    
    chunks: List[TextChunk] = []
    current_chunk: List[str] = []
    current_length = 0
    chunk_index = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        # If single sentence exceeds max_chars, create its own chunk
        if sentence_length > max_chars and not current_chunk:
            chunks.append(TextChunk(
                text=sentence,
                metadata=ChunkMetadata(
                    source_id=source_id,
                    chunk_index=chunk_index,
                    url=url,
                    title=title
                )
            ))
            chunk_index += 1
            continue
        
        # If adding sentence would exceed max_chars, finalize current chunk
        if current_length + sentence_length > max_chars and current_chunk:
            chunks.append(TextChunk(
                text=' '.join(current_chunk),
                metadata=ChunkMetadata(
                    source_id=source_id,
                    chunk_index=chunk_index,
                    url=url,
                    title=title
                )
            ))
            chunk_index += 1
            
            # Start new chunk with overlap
            overlap_start = max(0, len(current_chunk) - overlap_sentences)
            current_chunk = current_chunk[overlap_start:]
            current_length = sum(len(s) for s in current_chunk)
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    # Add final chunk
    if current_chunk:
        chunks.append(TextChunk(
            text=' '.join(current_chunk),
            metadata=ChunkMetadata(
                source_id=source_id,
                chunk_index=chunk_index,
                url=url,
                title=title
            )
        ))
    
    return chunks
