import {
  formatChunkId,
  formatChunksForLLM,
  extractCitationIds,
  buildCitationMap,
  replaceCitationsInText,
  formatCitationList,
  processAnalysisWithAttribution,
  ATTRIBUTION_SYSTEM_PROMPT,
  type ChunkReference,
} from '../attributionUtils';

describe('attributionUtils', () => {
  const mockChunks = [
    {
      text: 'First chunk content about quantum computing.',
      metadata: {
        sourceId: 'source-1',
        chunkIndex: 0,
        url: 'https://example.com/article1',
        title: 'Quantum Computing Basics',
      },
    },
    {
      text: 'Second chunk content about algorithms.',
      metadata: {
        sourceId: 'source-1',
        chunkIndex: 1,
        url: 'https://example.com/article1',
        title: 'Quantum Computing Basics',
      },
    },
    {
      text: 'Third chunk from different source.',
      metadata: {
        sourceId: 'source-2',
        chunkIndex: 0,
        url: 'https://example.com/article2',
        title: 'Advanced Algorithms',
      },
    },
  ];

  describe('formatChunkId', () => {
    it('should format chunk ID correctly', () => {
      expect(formatChunkId('source-1', 0)).toBe('[S1:C0]');
      expect(formatChunkId('source-2', 3)).toBe('[S2:C3]');
      expect(formatChunkId('source-123', 5)).toBe('[S123:C5]');
    });

    it('should handle non-numeric source IDs', () => {
      expect(formatChunkId('abc', 0)).toBe('[S0:C0]');
      expect(formatChunkId('source', 1)).toBe('[S0:C1]');
    });
  });

  describe('formatChunksForLLM', () => {
    it('should format chunks with IDs', () => {
      const formatted = formatChunksForLLM(mockChunks);
      
      expect(formatted).toContain('[S1:C0] First chunk content');
      expect(formatted).toContain('[S1:C1] Second chunk content');
      expect(formatted).toContain('[S2:C0] Third chunk from different source');
    });

    it('should separate chunks with double newlines', () => {
      const formatted = formatChunksForLLM(mockChunks);
      expect(formatted.split('\n\n')).toHaveLength(3);
    });

    it('should handle empty chunks array', () => {
      const formatted = formatChunksForLLM([]);
      expect(formatted).toBe('');
    });
  });

  describe('extractCitationIds', () => {
    it('should extract citation IDs from text', () => {
      const text = 'Quantum computing is powerful [S1:C0]. Algorithms are complex [S2:C0].';
      const ids = extractCitationIds(text);
      
      expect(ids).toEqual(['[S1:C0]', '[S2:C0]']);
    });

    it('should handle multiple citations', () => {
      const text = 'Text [S1:C0] more text [S1:C1] and [S2:C0].';
      const ids = extractCitationIds(text);
      
      expect(ids).toHaveLength(3);
    });

    it('should return empty array if no citations', () => {
      const text = 'Text without citations.';
      const ids = extractCitationIds(text);
      
      expect(ids).toEqual([]);
    });
  });

  describe('buildCitationMap', () => {
    it('should build citation map from chunks', () => {
      const map = buildCitationMap(mockChunks);
      
      expect(map.size).toBe(3);
      expect(map.get('[S1:C0]')).toEqual({
        id: 1,
        title: 'Quantum Computing Basics',
        url: 'https://example.com/article1',
        sourceId: 'source-1',
      });
      expect(map.get('[S2:C0]')).toEqual({
        id: 2,
        title: 'Advanced Algorithms',
        url: 'https://example.com/article2',
        sourceId: 'source-2',
      });
    });

    it('should assign same citation ID to chunks from same source', () => {
      const map = buildCitationMap(mockChunks);
      
      const citation1 = map.get('[S1:C0]');
      const citation2 = map.get('[S1:C1]');
      
      expect(citation1?.id).toBe(citation2?.id);
    });

    it('should handle chunks without URL or title', () => {
      const chunks = [{
        text: 'Content',
        metadata: { sourceId: 'source-1', chunkIndex: 0 },
      }];
      
      const map = buildCitationMap(chunks);
      const citation = map.get('[S1:C0]');
      
      expect(citation?.title).toBe('Untitled');
      expect(citation?.url).toBe('');
    });
  });

  describe('replaceCitationsInText', () => {
    it('should replace chunk IDs with citation numbers', () => {
      const map = buildCitationMap(mockChunks);
      const text = 'Quantum computing [S1:C0] and algorithms [S2:C0].';
      
      const { text: replaced, usedCitations } = replaceCitationsInText(text, map);
      
      expect(replaced).toBe('Quantum computing [1] and algorithms [2].');
      expect(usedCitations).toHaveLength(2);
    });

    it('should only include citations that are used', () => {
      const map = buildCitationMap(mockChunks);
      const text = 'Only mentioning first source [S1:C0].';
      
      const { usedCitations } = replaceCitationsInText(text, map);
      
      expect(usedCitations).toHaveLength(1);
      expect(usedCitations[0].id).toBe(1);
    });

    it('should deduplicate citations from same source', () => {
      const map = buildCitationMap(mockChunks);
      const text = 'First [S1:C0] and second [S1:C1] from same source.';
      
      const { text: replaced, usedCitations } = replaceCitationsInText(text, map);
      
      expect(replaced).toBe('First [1] and second [1] from same source.');
      expect(usedCitations).toHaveLength(1);
    });

    it('should sort citations by ID', () => {
      const map = buildCitationMap(mockChunks);
      const text = 'Second [S2:C0] then first [S1:C0].';
      
      const { usedCitations } = replaceCitationsInText(text, map);
      
      expect(usedCitations[0].id).toBe(1);
      expect(usedCitations[1].id).toBe(2);
    });
  });

  describe('formatCitationList', () => {
    it('should format citation list', () => {
      const citations = [
        { id: 1, title: 'Article 1', url: 'https://example.com/1', sourceId: 'source-1' },
        { id: 2, title: 'Article 2', url: 'https://example.com/2', sourceId: 'source-2' },
      ];
      
      const formatted = formatCitationList(citations);
      
      expect(formatted).toContain('[1] Article 1 — https://example.com/1');
      expect(formatted).toContain('[2] Article 2 — https://example.com/2');
      expect(formatted).toContain('Sources:');
    });

    it('should handle citations without URLs', () => {
      const citations = [
        { id: 1, title: 'Article 1', url: '', sourceId: 'source-1' },
      ];
      
      const formatted = formatCitationList(citations);
      
      expect(formatted).toContain('[1] Article 1');
      expect(formatted).not.toContain('—');
    });

    it('should return empty string for no citations', () => {
      const formatted = formatCitationList([]);
      expect(formatted).toBe('');
    });
  });

  describe('processAnalysisWithAttribution', () => {
    it('should process analysis text with full attribution', () => {
      const analysisText = 'Quantum computing is powerful [S1:C0]. Algorithms are important [S2:C0].';
      
      const result = processAnalysisWithAttribution(analysisText, mockChunks);
      
      expect(result.text).toContain('Quantum computing is powerful [1]');
      expect(result.text).toContain('Algorithms are important [2]');
      expect(result.text).toContain('Sources:');
      expect(result.text).toContain('[1] Quantum Computing Basics');
      expect(result.text).toContain('[2] Advanced Algorithms');
      expect(result.citations).toHaveLength(2);
    });

    it('should only include used citations in output', () => {
      const analysisText = 'Only first source [S1:C0].';
      
      const result = processAnalysisWithAttribution(analysisText, mockChunks);
      
      expect(result.citations).toHaveLength(1);
      expect(result.text).toContain('[1] Quantum Computing Basics');
      expect(result.text).not.toContain('Advanced Algorithms');
    });
  });

  describe('ATTRIBUTION_SYSTEM_PROMPT', () => {
    it('should contain citation instructions', () => {
      expect(ATTRIBUTION_SYSTEM_PROMPT).toContain('cite');
      expect(ATTRIBUTION_SYSTEM_PROMPT).toContain('[S');
      expect(ATTRIBUTION_SYSTEM_PROMPT).toContain(':C');
    });
  });
});
