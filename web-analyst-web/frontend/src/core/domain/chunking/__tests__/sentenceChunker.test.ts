import { chunkText, TextChunk } from '../sentenceChunker';

describe('sentenceChunker', () => {
  describe('chunkText', () => {
    it('should handle empty text', () => {
      const chunks = chunkText('', 'source-1');
      expect(chunks).toEqual([]);
    });

    it('should handle whitespace-only text', () => {
      const chunks = chunkText('   \n\n  ', 'source-1');
      expect(chunks).toEqual([]);
    });

    it('should chunk short text into single chunk', () => {
      const text = 'This is a short sentence. This is another one.';
      const chunks = chunkText(text, 'source-1', 'http://example.com', 'Example');

      expect(chunks).toHaveLength(1);
      expect(chunks[0].text).toBe(text);
      expect(chunks[0].metadata).toEqual({
        sourceId: 'source-1',
        chunkIndex: 0,
        url: 'http://example.com',
        title: 'Example',
      });
    });

    it('should chunk long text into multiple chunks', () => {
      // Create text that exceeds maxChars (1500)
      const sentence = 'This is a sentence that will be repeated many times. ';
      const text = sentence.repeat(50); // ~2500 chars

      const chunks = chunkText(text, 'source-1');

      expect(chunks.length).toBeGreaterThan(1);
      expect(chunks.every(c => c.text.length <= 1600)).toBe(true); // Allow some buffer
      expect(chunks.every(c => c.metadata.sourceId === 'source-1')).toBe(true);
    });

    it('should maintain consistent chunk ordering', () => {
      const text = 'First sentence. Second sentence. Third sentence. Fourth sentence.';
      const chunks = chunkText(text, 'source-1');

      for (let i = 0; i < chunks.length; i++) {
        expect(chunks[i].metadata.chunkIndex).toBe(i);
      }
    });

    it('should include overlap between chunks', () => {
      // Create text that will split into 2 chunks
      const sentence = 'This is a sentence. ';
      const text = sentence.repeat(100); // ~2000 chars

      const chunks = chunkText(text, 'source-1', undefined, undefined, {
        maxChars: 1000,
        overlapSentences: 1,
      });

      expect(chunks.length).toBeGreaterThan(1);
      
      // Check that there's overlap (last sentence of chunk N appears in chunk N+1)
      if (chunks.length >= 2) {
        const chunk1Sentences = chunks[0].text.split('. ').filter(s => s.length > 0);
        const chunk2Sentences = chunks[1].text.split('. ').filter(s => s.length > 0);
        
        const lastSentenceChunk1 = chunk1Sentences[chunk1Sentences.length - 1];
        const firstSentenceChunk2 = chunk2Sentences[0];
        
        expect(firstSentenceChunk2).toContain(lastSentenceChunk1.substring(0, 10));
      }
    });

    it('should handle punctuation edge cases', () => {
      const text = 'Dr. Smith works at U.S. Labs! Is that correct? Yes. No problem.';
      const chunks = chunkText(text, 'source-1');

      expect(chunks).toHaveLength(1);
      expect(chunks[0].text).toBe(text);
    });

    it('should handle text with only periods', () => {
      const text = 'First. Second. Third. Fourth. Fifth.';
      const chunks = chunkText(text, 'source-1', undefined, undefined, {
        maxChars: 20,
      });

      expect(chunks.length).toBeGreaterThan(1);
      expect(chunks.every(c => c.text.length > 0)).toBe(true);
    });

    it('should handle text with mixed punctuation', () => {
      const text = 'Question? Answer! Statement. Another question? Final answer!';
      const chunks = chunkText(text, 'source-1');

      expect(chunks).toHaveLength(1);
      expect(chunks[0].text).toBe(text);
    });

    it('should handle single very long sentence', () => {
      const longSentence = 'A'.repeat(2000) + '.';
      const chunks = chunkText(longSentence, 'source-1');

      expect(chunks).toHaveLength(1);
      expect(chunks[0].text).toBe(longSentence);
      expect(chunks[0].metadata.chunkIndex).toBe(0);
    });

    it('should not create empty chunks', () => {
      const text = 'Sentence one. Sentence two. Sentence three.';
      const chunks = chunkText(text, 'source-1');

      expect(chunks.every(c => c.text.trim().length > 0)).toBe(true);
    });

    it('should handle newlines as sentence boundaries', () => {
      const text = 'First line.\nSecond line.\nThird line.';
      const chunks = chunkText(text, 'source-1');

      expect(chunks).toHaveLength(1);
      expect(chunks[0].text).toContain('First line');
      expect(chunks[0].text).toContain('Second line');
      expect(chunks[0].text).toContain('Third line');
    });

    it('should merge small fragments', () => {
      const text = 'A. B. C. D. E. F. G. H. I. J.';
      const chunks = chunkText(text, 'source-1', undefined, undefined, {
        maxChars: 50,
      });

      // Should merge small sentences into chunks
      expect(chunks.length).toBeGreaterThan(0);
      expect(chunks.every(c => c.text.length > 0)).toBe(true);
    });

    it('should handle text without sentence terminators', () => {
      const text = 'This is text without proper punctuation';
      const chunks = chunkText(text, 'source-1');

      expect(chunks).toHaveLength(1);
      expect(chunks[0].text).toBe(text);
    });

    it('should preserve metadata across all chunks', () => {
      const sentence = 'This is a test sentence. ';
      const text = sentence.repeat(100);
      
      const chunks = chunkText(text, 'source-123', 'http://test.com', 'Test Title', {
        maxChars: 500,
      });

      expect(chunks.length).toBeGreaterThan(1);
      chunks.forEach(chunk => {
        expect(chunk.metadata.sourceId).toBe('source-123');
        expect(chunk.metadata.url).toBe('http://test.com');
        expect(chunk.metadata.title).toBe('Test Title');
      });
    });
  });
});
