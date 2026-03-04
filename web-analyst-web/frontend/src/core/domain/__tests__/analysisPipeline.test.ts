import { chunkText } from '../chunking';
import {
  formatChunksForLLM,
  processAnalysisWithAttribution,
  buildCitationMap,
} from '../attribution';

describe('Analysis Pipeline Integration', () => {
  const sampleText = `
    Quantum computing uses quantum bits or qubits. These qubits can exist in superposition.
    This allows quantum computers to process multiple states simultaneously.
    Quantum entanglement enables qubits to be correlated in unique ways.
    Shor's algorithm can factor large numbers exponentially faster.
    Grover's algorithm provides quadratic speedup for search problems.
  `.trim();

  describe('Chunking → Attribution Pipeline', () => {
    it('should chunk text and preserve metadata for attribution', () => {
      const chunks = chunkText(
        sampleText,
        'source-1',
        'https://example.com/quantum',
        'Quantum Computing Guide',
        { maxChars: 200 }
      );

      expect(chunks.length).toBeGreaterThan(0);
      chunks.forEach((chunk, index) => {
        expect(chunk.metadata.sourceId).toBe('source-1');
        expect(chunk.metadata.chunkIndex).toBe(index);
        expect(chunk.metadata.url).toBe('https://example.com/quantum');
        expect(chunk.metadata.title).toBe('Quantum Computing Guide');
      });
    });

    it('should format chunks for LLM with proper IDs', () => {
      const chunks = chunkText(sampleText, 'source-1', 'https://example.com', 'Title');
      const formatted = formatChunksForLLM(chunks);

      expect(formatted).toContain('[S1:C0]');
      expect(formatted).toContain('quantum');
    });

    it('should process complete attribution pipeline', () => {
      const chunks = chunkText(
        sampleText,
        'source-1',
        'https://example.com/quantum',
        'Quantum Guide',
        { maxChars: 200 }
      );

      const llmResponse = `
        Quantum computing uses qubits [S1:C0]. 
        These enable superposition [S1:C0].
      `.trim();

      const result = processAnalysisWithAttribution(llmResponse, chunks);

      expect(result.text).toContain('[1]');
      expect(result.text).toContain('Sources:');
      expect(result.text).toContain('Quantum Guide');
      expect(result.citations).toHaveLength(1);
      expect(result.citations[0].title).toBe('Quantum Guide');
    });

    it('should handle multiple sources in pipeline', () => {
      const chunks1 = chunkText(
        'First source content.',
        'source-1',
        'https://example.com/1',
        'Source 1'
      );
      const chunks2 = chunkText(
        'Second source content.',
        'source-2',
        'https://example.com/2',
        'Source 2'
      );

      const allChunks = [...chunks1, ...chunks2];
      const llmResponse = 'First [S1:C0] and second [S2:C0].';

      const result = processAnalysisWithAttribution(llmResponse, allChunks);

      expect(result.citations).toHaveLength(2);
      expect(result.text).toContain('[1]');
      expect(result.text).toContain('[2]');
    });
  });

  describe('Chunking Constraints', () => {
    it('should respect max chunk size', () => {
      const longText = 'A sentence. '.repeat(200);
      const chunks = chunkText(longText, 'source-1', '', '', { maxChars: 500 });

      chunks.forEach(chunk => {
        expect(chunk.text.length).toBeLessThanOrEqual(600); // Allow some buffer
      });
    });

    it('should create overlapping chunks', () => {
      const text = 'First sentence. Second sentence. Third sentence. Fourth sentence.';
      const chunks = chunkText(text, 'source-1', '', '', {
        maxChars: 50,
        overlapSentences: 1,
      });

      if (chunks.length >= 2) {
        const chunk1Sentences = chunks[0].text.split('. ');
        const chunk2Sentences = chunks[1].text.split('. ');

        // Check for overlap
        const lastSentence1 = chunk1Sentences[chunk1Sentences.length - 1];
        const firstSentence2 = chunk2Sentences[0];

        expect(firstSentence2).toContain(lastSentence1.substring(0, 5));
      }
    });

    it('should maintain chunk order', () => {
      const chunks = chunkText(sampleText, 'source-1', '', '', { maxChars: 100 });

      for (let i = 0; i < chunks.length; i++) {
        expect(chunks[i].metadata.chunkIndex).toBe(i);
      }
    });

    it('should not create empty chunks', () => {
      const chunks = chunkText(sampleText, 'source-1');

      chunks.forEach(chunk => {
        expect(chunk.text.trim().length).toBeGreaterThan(0);
      });
    });
  });

  describe('Citation Generation', () => {
    it('should generate correct citation IDs', () => {
      const chunks = chunkText('Test text.', 'source-1', 'url', 'title');
      const map = buildCitationMap(chunks);

      const citation = map.get('[S1:C0]');
      expect(citation).toBeDefined();
      expect(citation?.id).toBe(1);
      expect(citation?.title).toBe('title');
      expect(citation?.url).toBe('url');
    });

    it('should deduplicate citations from same source', () => {
      const chunks = chunkText(
        'First sentence. Second sentence. Third sentence.',
        'source-1',
        'url',
        'title',
        { maxChars: 30 }
      );

      const map = buildCitationMap(chunks);
      const citations = Array.from(map.values());
      const uniqueIds = new Set(citations.map(c => c.id));

      expect(uniqueIds.size).toBe(1); // All chunks from same source
    });

    it('should reference correct sources', () => {
      const chunks1 = chunkText('Content 1.', 'source-1', 'url1', 'Title 1');
      const chunks2 = chunkText('Content 2.', 'source-2', 'url2', 'Title 2');

      const allChunks = [...chunks1, ...chunks2];
      const llmResponse = 'Statement [S1:C0] and [S2:C0].';

      const result = processAnalysisWithAttribution(llmResponse, allChunks);

      expect(result.citations[0].title).toBe('Title 1');
      expect(result.citations[1].title).toBe('Title 2');
      expect(result.citations[0].url).toBe('url1');
      expect(result.citations[1].url).toBe('url2');
    });

    it('should only include used citations', () => {
      const chunks1 = chunkText('Content 1.', 'source-1', 'url1', 'Title 1');
      const chunks2 = chunkText('Content 2.', 'source-2', 'url2', 'Title 2');
      const chunks3 = chunkText('Content 3.', 'source-3', 'url3', 'Title 3');

      const allChunks = [...chunks1, ...chunks2, ...chunks3];
      const llmResponse = 'Only first [S1:C0] and second [S2:C0].';

      const result = processAnalysisWithAttribution(llmResponse, allChunks);

      expect(result.citations).toHaveLength(2);
      expect(result.citations.find(c => c.title === 'Title 3')).toBeUndefined();
    });
  });

  describe('End-to-End Pipeline', () => {
    it('should handle complete analysis workflow', () => {
      // 1. Chunk sources
      const source1Chunks = chunkText(
        'Quantum computing is revolutionary. It uses qubits.',
        'source-1',
        'https://quantum.com',
        'Quantum Basics'
      );

      const source2Chunks = chunkText(
        'Machine learning enables AI. Neural networks are powerful.',
        'source-2',
        'https://ml.com',
        'ML Guide'
      );

      const allChunks = [...source1Chunks, ...source2Chunks];

      // 2. Format for LLM
      const context = formatChunksForLLM(allChunks);
      expect(context).toContain('[S1:C0]');
      expect(context).toContain('[S2:C0]');

      // 3. Simulate LLM response
      const llmResponse = `
        Quantum computing is revolutionary [S1:C0].
        Machine learning enables AI [S2:C0].
      `.trim();

      // 4. Process attribution
      const result = processAnalysisWithAttribution(llmResponse, allChunks);

      // 5. Verify output
      expect(result.text).toContain('[1]');
      expect(result.text).toContain('[2]');
      expect(result.text).toContain('Sources:');
      expect(result.text).toContain('Quantum Basics');
      expect(result.text).toContain('ML Guide');
      expect(result.citations).toHaveLength(2);
    });

    it('should handle edge cases in pipeline', () => {
      // Empty text
      const emptyChunks = chunkText('', 'source-1');
      expect(emptyChunks).toHaveLength(0);

      // Single word
      const singleWord = chunkText('Word', 'source-1');
      expect(singleWord).toHaveLength(1);

      // Very long text
      const longText = 'Sentence. '.repeat(1000);
      const longChunks = chunkText(longText, 'source-1');
      expect(longChunks.length).toBeGreaterThan(1);
    });
  });
});
