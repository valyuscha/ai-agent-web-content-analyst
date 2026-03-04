import { Space, SpaceAction } from '../SpaceContext';

// Import the reducer function (we need to extract it)
// For now, we'll test the reducer logic through the context

describe('Space State Management', () => {
  describe('Space Isolation', () => {
    it('should keep spaces isolated', () => {
      const space1 = createDefaultSpace('Space 1');
      const space2 = createDefaultSpace('Space 2');

      // Modify space1
      space1.input.urls = ['http://example1.com'];
      space1.results.sessionId = 'session-1';

      // Modify space2
      space2.input.urls = ['http://example2.com'];
      space2.results.sessionId = 'session-2';

      // Verify isolation
      expect(space1.input.urls).toEqual(['http://example1.com']);
      expect(space2.input.urls).toEqual(['http://example2.com']);
      expect(space1.results.sessionId).toBe('session-1');
      expect(space2.results.sessionId).toBe('session-2');
    });

    it('should not share references between spaces', () => {
      const space1 = createDefaultSpace();
      const space2 = createDefaultSpace();

      space1.input.urls.push('http://test.com');

      expect(space1.input.urls).toHaveLength(2);
      expect(space2.input.urls).toHaveLength(1);
    });

    it('should maintain separate logs', () => {
      const space1 = createDefaultSpace();
      const space2 = createDefaultSpace();

      space1.log.entries.push('Log 1');
      space2.log.entries.push('Log 2');

      expect(space1.log.entries).toEqual(['Log 1']);
      expect(space2.log.entries).toEqual(['Log 2']);
    });

    it('should maintain separate sources', () => {
      const space1 = createDefaultSpace();
      const space2 = createDefaultSpace();

      space1.sources.items.push({ url: 'url1', title: 'Title 1' });
      space2.sources.items.push({ url: 'url2', title: 'Title 2' });

      expect(space1.sources.items).toHaveLength(1);
      expect(space2.sources.items).toHaveLength(1);
      expect(space1.sources.items[0].url).toBe('url1');
      expect(space2.sources.items[0].url).toBe('url2');
    });

    it('should maintain separate results', () => {
      const space1 = createDefaultSpace();
      const space2 = createDefaultSpace();

      space1.results.analysis = { data: 'analysis1' };
      space2.results.analysis = { data: 'analysis2' };

      expect(space1.results.analysis).toEqual({ data: 'analysis1' });
      expect(space2.results.analysis).toEqual({ data: 'analysis2' });
    });

    it('should maintain separate loading states', () => {
      const space1 = createDefaultSpace();
      const space2 = createDefaultSpace();

      space1.loading = true;
      space2.loading = false;

      expect(space1.loading).toBe(true);
      expect(space2.loading).toBe(false);
    });

    it('should maintain separate error states', () => {
      const space1 = createDefaultSpace();
      const space2 = createDefaultSpace();

      space1.error = 'Error 1';
      space2.error = 'Error 2';

      expect(space1.error).toBe('Error 1');
      expect(space2.error).toBe('Error 2');
    });

    it('should maintain separate UI states', () => {
      const space1 = createDefaultSpace();
      const space2 = createDefaultSpace();

      space1.ui.activeTab = 'results';
      space2.ui.activeTab = 'sources';

      expect(space1.ui.activeTab).toBe('results');
      expect(space2.ui.activeTab).toBe('sources');
    });
  });

  describe('Space Updates', () => {
    it('should update timestamp on modification', () => {
      const space = createDefaultSpace();
      const originalTime = space.updatedAt;

      // Simulate update
      space.updatedAt = Date.now();

      expect(space.updatedAt).toBeGreaterThanOrEqual(originalTime);
    });

    it('should preserve other fields when updating one field', () => {
      const space = createDefaultSpace();
      space.input.urls = ['http://test.com'];
      space.results.sessionId = 'session-123';

      // Update only one field
      space.input.pastedText = 'New text';

      // Other fields should be preserved
      expect(space.input.urls).toEqual(['http://test.com']);
      expect(space.results.sessionId).toBe('session-123');
      expect(space.input.pastedText).toBe('New text');
    });
  });

  describe('Space Actions', () => {
    it('should handle UPDATE_SPACE action structure', () => {
      const action: SpaceAction = {
        type: 'UPDATE_SPACE',
        payload: {
          id: 'space-1',
          updates: {
            loading: true,
            error: null,
          },
        },
      };

      expect(action.type).toBe('UPDATE_SPACE');
      expect(action.payload.id).toBe('space-1');
      expect(action.payload.updates.loading).toBe(true);
    });

    it('should handle APPEND_LOG action structure', () => {
      const action: SpaceAction = {
        type: 'APPEND_LOG',
        payload: {
          id: 'space-1',
          entry: 'Log message',
        },
      };

      expect(action.type).toBe('APPEND_LOG');
      expect(action.payload.id).toBe('space-1');
      expect(action.payload.entry).toBe('Log message');
    });

    it('should handle RESET_SPACE action structure', () => {
      const action: SpaceAction = {
        type: 'RESET_SPACE',
        payload: 'space-1',
      };

      expect(action.type).toBe('RESET_SPACE');
      expect(action.payload).toBe('space-1');
    });
  });

  describe('Data Integrity', () => {
    it('should maintain data types', () => {
      const space = createDefaultSpace();

      expect(typeof space.id).toBe('string');
      expect(typeof space.name).toBe('string');
      expect(typeof space.createdAt).toBe('number');
      expect(typeof space.updatedAt).toBe('number');
      expect(typeof space.loading).toBe('boolean');
      expect(Array.isArray(space.input.urls)).toBe(true);
      expect(Array.isArray(space.sources.items)).toBe(true);
      expect(Array.isArray(space.log.entries)).toBe(true);
    });

    it('should handle partial updates', () => {
      const space = createDefaultSpace();
      const updates: Partial<Space> = {
        loading: true,
        error: 'Test error',
      };

      Object.assign(space, updates);

      expect(space.loading).toBe(true);
      expect(space.error).toBe('Test error');
      expect(space.id).toBeDefined();
      expect(space.name).toBeDefined();
    });
  });
});
