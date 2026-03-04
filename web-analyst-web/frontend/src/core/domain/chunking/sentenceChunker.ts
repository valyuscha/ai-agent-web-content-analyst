export interface ChunkMetadata {
  sourceId: string;
  chunkIndex: number;
  url?: string;
  title?: string;
}

export interface TextChunk {
  text: string;
  metadata: ChunkMetadata;
}

export interface ChunkingOptions {
  maxChars?: number;
  overlapSentences?: number;
}

function splitIntoSentences(text: string): string[] {
  // Try Intl.Segmenter if available (modern browsers)
  if (typeof Intl !== 'undefined' && 'Segmenter' in Intl) {
    try {
      const segmenter = new (Intl as any).Segmenter('en', { granularity: 'sentence' });
      const segments = segmenter.segment(text);
      return Array.from(segments, (s: any) => s.segment.trim()).filter((s: string) => s.length > 0);
    } catch (e) {
      // Fall through to regex
    }
  }

  // Regex fallback: split on sentence boundaries
  // Handles: . ! ? followed by space/newline, but not abbreviations like "Dr." or "U.S."
  const sentences = text
    .replace(/([.!?])\s+(?=[A-Z])/g, '$1|')
    .replace(/([.!?])(\n+)/g, '$1|')
    .split('|')
    .map(s => s.trim())
    .filter(s => s.length > 0);

  return sentences;
}

export function chunkText(
  text: string,
  sourceId: string,
  sourceUrl?: string,
  sourceTitle?: string,
  options: ChunkingOptions = {}
): TextChunk[] {
  const maxChars = options.maxChars || 1500;
  const overlapSentences = options.overlapSentences || 1;

  if (!text || text.trim().length === 0) {
    return [];
  }

  const sentences = splitIntoSentences(text);
  
  if (sentences.length === 0) {
    return [];
  }

  const chunks: TextChunk[] = [];
  let currentChunk: string[] = [];
  let currentLength = 0;
  let chunkIndex = 0;

  for (let i = 0; i < sentences.length; i++) {
    const sentence = sentences[i];
    const sentenceLength = sentence.length;

    // If single sentence exceeds maxChars, split it as its own chunk
    if (sentenceLength > maxChars && currentChunk.length === 0) {
      chunks.push({
        text: sentence,
        metadata: {
          sourceId,
          chunkIndex: chunkIndex++,
          url: sourceUrl,
          title: sourceTitle,
        },
      });
      continue;
    }

    // If adding this sentence would exceed maxChars, finalize current chunk
    if (currentLength + sentenceLength > maxChars && currentChunk.length > 0) {
      chunks.push({
        text: currentChunk.join(' '),
        metadata: {
          sourceId,
          chunkIndex: chunkIndex++,
          url: sourceUrl,
          title: sourceTitle,
        },
      });

      // Start new chunk with overlap
      const overlapStart = Math.max(0, currentChunk.length - overlapSentences);
      currentChunk = currentChunk.slice(overlapStart);
      currentLength = currentChunk.reduce((sum, s) => sum + s.length, 0);
    }

    currentChunk.push(sentence);
    currentLength += sentenceLength;
  }

  // Add final chunk if not empty
  if (currentChunk.length > 0) {
    chunks.push({
      text: currentChunk.join(' '),
      metadata: {
        sourceId,
        chunkIndex: chunkIndex++,
        url: sourceUrl,
        title: sourceTitle,
      },
    });
  }

  return chunks;
}
