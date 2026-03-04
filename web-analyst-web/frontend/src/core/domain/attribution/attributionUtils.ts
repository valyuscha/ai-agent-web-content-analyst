export interface ChunkReference {
  sourceId: string;
  chunkIndex: number;
  url?: string;
  title?: string;
}

export interface FormattedChunk {
  id: string;
  text: string;
  reference: ChunkReference;
}

export interface Citation {
  id: number;
  title: string;
  url: string;
  sourceId: string;
}

export function formatChunkId(sourceId: string, chunkIndex: number): string {
  const sourceNum = sourceId.replace(/\D/g, '') || '0';
  return `[S${sourceNum}:C${chunkIndex}]`;
}

export function formatChunksForLLM(chunks: Array<{ text: string; metadata: ChunkReference }>): string {
  return chunks
    .map(chunk => {
      const id = formatChunkId(chunk.metadata.sourceId, chunk.metadata.chunkIndex);
      return `${id} ${chunk.text}`;
    })
    .join('\n\n');
}

export function extractCitationIds(text: string): string[] {
  const regex = /\[S(\d+):C(\d+)\]/g;
  const matches: string[] = [];
  let match;
  while ((match = regex.exec(text)) !== null) {
    matches.push(match[0]);
  }
  return matches;
}

export function buildCitationMap(
  chunks: Array<{ text: string; metadata: ChunkReference }>
): Map<string, Citation> {
  const citationMap = new Map<string, Citation>();
  const sourceMap = new Map<string, { title: string; url: string; count: number }>();

  chunks.forEach(chunk => {
    const { sourceId, url, title } = chunk.metadata;
    if (!sourceMap.has(sourceId)) {
      sourceMap.set(sourceId, {
        title: title || 'Untitled',
        url: url || '',
        count: sourceMap.size + 1,
      });
    }
  });

  chunks.forEach(chunk => {
    const chunkId = formatChunkId(chunk.metadata.sourceId, chunk.metadata.chunkIndex);
    const sourceInfo = sourceMap.get(chunk.metadata.sourceId)!;
    
    citationMap.set(chunkId, {
      id: sourceInfo.count,
      title: sourceInfo.title,
      url: sourceInfo.url,
      sourceId: chunk.metadata.sourceId,
    });
  });

  return citationMap;
}

export function replaceCitationsInText(
  text: string,
  citationMap: Map<string, Citation>
): { text: string; usedCitations: Citation[] } {
  const usedCitationIds = new Set<string>();
  const usedCitations: Citation[] = [];

  const replacedText = text.replace(/\[S(\d+):C(\d+)\]/g, (match) => {
    const citation = citationMap.get(match);
    if (citation) {
      const citationKey = `${citation.sourceId}`;
      if (!usedCitationIds.has(citationKey)) {
        usedCitationIds.add(citationKey);
        usedCitations.push(citation);
      }
      return `[${citation.id}]`;
    }
    return match;
  });

  usedCitations.sort((a, b) => a.id - b.id);

  return { text: replacedText, usedCitations };
}

export function formatCitationList(citations: Citation[]): string {
  if (citations.length === 0) return '';

  return '\n\nSources:\n' + citations
    .map(c => `[${c.id}] ${c.title}${c.url ? ' — ' + c.url : ''}`)
    .join('\n');
}

export function processAnalysisWithAttribution(
  analysisText: string,
  chunks: Array<{ text: string; metadata: ChunkReference }>
): { text: string; citations: Citation[] } {
  const citationMap = buildCitationMap(chunks);
  const { text, usedCitations } = replaceCitationsInText(analysisText, citationMap);
  
  return {
    text: text + formatCitationList(usedCitations),
    citations: usedCitations,
  };
}

export const ATTRIBUTION_SYSTEM_PROMPT = `
When providing your analysis, cite the sources by including the chunk ID in square brackets immediately after the relevant statement.

For example:
- "The research shows significant improvements [S1:C2]."
- "According to the study, the results were positive [S2:C0]."

Always cite the specific chunk that supports your statement. Use the exact chunk ID format provided in the context.
`.trim();
