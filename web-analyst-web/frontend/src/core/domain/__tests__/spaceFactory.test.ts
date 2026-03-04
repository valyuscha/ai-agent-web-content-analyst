import { createDefaultSpace, deepCloneSpace } from '../spaceFactory';

describe('spaceFactory', () => {
  describe('createDefaultSpace', () => {
    it('should create space with default values', () => {
      const space = createDefaultSpace();

      expect(space.id).toBeDefined();
      expect(space.name).toBe('Space 1');
      expect(space.createdAt).toBeDefined();
      expect(space.updatedAt).toBeDefined();
      expect(space.input.urls).toEqual(['']);
      expect(space.input.pastedText).toBe('');
      expect(space.input.analysisMode).toBe('General summary');
      expect(space.input.tone).toBe('formal');
      expect(space.sources.items).toEqual([]);
      expect(space.results.sessionId).toBeNull();
      expect(space.loading).toBe(false);
      expect(space.error).toBeNull();
    });

    it('should create space with custom name', () => {
      const space = createDefaultSpace('Custom Space');
      expect(space.name).toBe('Custom Space');
    });

    it('should create space with index', () => {
      const space = createDefaultSpace(undefined, 5);
      expect(space.name).toBe('Space 5');
    });

    it('should generate unique IDs', () => {
      const space1 = createDefaultSpace();
      const space2 = createDefaultSpace();
      expect(space1.id).not.toBe(space2.id);
    });

    it('should set timestamps', () => {
      const before = Date.now();
      const space = createDefaultSpace();
      const after = Date.now();

      expect(space.createdAt).toBeGreaterThanOrEqual(before);
      expect(space.createdAt).toBeLessThanOrEqual(after);
      expect(space.updatedAt).toBe(space.createdAt);
    });
  });

  describe('deepCloneSpace', () => {
    it('should clone space with new ID', () => {
      const original = createDefaultSpace('Original');
      const cloned = deepCloneSpace(original);

      expect(cloned.id).not.toBe(original.id);
      expect(cloned.name).toBe('Copy of Original');
    });

    it('should clone with custom name', () => {
      const original = createDefaultSpace('Original');
      const cloned = deepCloneSpace(original, 'Custom Clone');

      expect(cloned.name).toBe('Custom Clone');
    });

    it('should deep clone nested objects', () => {
      const original = createDefaultSpace();
      original.input.urls = ['http://example.com'];
      original.sources.items = [{ url: 'test', title: 'Test' }];

      const cloned = deepCloneSpace(original);

      // Modify cloned
      cloned.input.urls.push('http://another.com');
      cloned.sources.items.push({ url: 'test2', title: 'Test2' });

      // Original should be unchanged
      expect(original.input.urls).toHaveLength(1);
      expect(original.sources.items).toHaveLength(1);
      expect(cloned.input.urls).toHaveLength(2);
      expect(cloned.sources.items).toHaveLength(2);
    });

    it('should update timestamps', () => {
      const original = createDefaultSpace();
      const originalTime = original.createdAt;

      // Wait a bit
      const cloned = deepCloneSpace(original);

      expect(cloned.createdAt).toBeGreaterThanOrEqual(originalTime);
      expect(cloned.updatedAt).toBe(cloned.createdAt);
    });

    it('should preserve all data', () => {
      const original = createDefaultSpace();
      original.input.urls = ['http://test.com'];
      original.input.pastedText = 'Test text';
      original.input.analysisMode = 'Deep analysis';
      original.input.tone = 'casual';
      original.results.sessionId = 'session-123';
      original.results.reportMarkdown = '# Report';
      original.email.subject = 'Test Subject';
      original.email.body = 'Test Body';
      original.log.entries = ['Log entry 1'];

      const cloned = deepCloneSpace(original);

      expect(cloned.input.urls).toEqual(original.input.urls);
      expect(cloned.input.pastedText).toBe(original.input.pastedText);
      expect(cloned.input.analysisMode).toBe(original.input.analysisMode);
      expect(cloned.input.tone).toBe(original.input.tone);
      expect(cloned.results.sessionId).toBe(original.results.sessionId);
      expect(cloned.results.reportMarkdown).toBe(original.results.reportMarkdown);
      expect(cloned.email.subject).toBe(original.email.subject);
      expect(cloned.email.body).toBe(original.email.body);
      expect(cloned.log.entries).toEqual(original.log.entries);
    });
  });
});
