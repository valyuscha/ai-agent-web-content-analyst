import { safeLoadSpaces, persistSpaces } from '../spaceStorage';
import { createDefaultSpace } from '../../domain/spaceFactory';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
});

describe('spaceStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('safeLoadSpaces', () => {
    it('should return default space when localStorage is empty', () => {
      const { spaces, activeSpaceId } = safeLoadSpaces();

      expect(spaces).toHaveLength(1);
      expect(spaces[0].name).toBe('Space 1');
      expect(activeSpaceId).toBe(spaces[0].id);
    });

    it('should load spaces from localStorage', () => {
      const space1 = createDefaultSpace('Space 1');
      const space2 = createDefaultSpace('Space 2');
      
      localStorage.setItem('wca.spaces.v1', JSON.stringify([space1, space2]));
      localStorage.setItem('wca.activeSpaceId.v1', space2.id);

      const { spaces, activeSpaceId } = safeLoadSpaces();

      expect(spaces).toHaveLength(2);
      expect(spaces[0].id).toBe(space1.id);
      expect(spaces[1].id).toBe(space2.id);
      expect(activeSpaceId).toBe(space2.id);
    });

    it('should validate loaded spaces', () => {
      const space = createDefaultSpace();
      localStorage.setItem('wca.spaces.v1', JSON.stringify([space]));

      const { spaces } = safeLoadSpaces();

      expect(spaces[0]).toMatchObject({
        id: expect.any(String),
        name: expect.any(String),
        createdAt: expect.any(Number),
        updatedAt: expect.any(Number),
        input: expect.any(Object),
        sources: expect.any(Object),
        results: expect.any(Object),
        email: expect.any(Object),
        log: expect.any(Object),
        ui: expect.any(Object),
        loading: expect.any(Boolean),
      });
    });

    it('should clear error if no sessionId', () => {
      const space = createDefaultSpace();
      space.error = 'Some error';
      space.results.sessionId = null;

      localStorage.setItem('wca.spaces.v1', JSON.stringify([space]));

      const { spaces } = safeLoadSpaces();

      expect(spaces[0].error).toBeNull();
    });

    it('should preserve error if sessionId exists', () => {
      const space = createDefaultSpace();
      space.error = 'Some error';
      space.results.sessionId = 'session-123';

      localStorage.setItem('wca.spaces.v1', JSON.stringify([space]));

      const { spaces } = safeLoadSpaces();

      expect(spaces[0].error).toBe('Some error');
    });

    it('should handle invalid activeSpaceId', () => {
      const space = createDefaultSpace();
      localStorage.setItem('wca.spaces.v1', JSON.stringify([space]));
      localStorage.setItem('wca.activeSpaceId.v1', 'invalid-id');

      const { activeSpaceId } = safeLoadSpaces();

      expect(activeSpaceId).toBe(space.id);
    });

    it('should handle corrupted data', () => {
      localStorage.setItem('wca.spaces.v1', 'invalid json');

      const { spaces, activeSpaceId } = safeLoadSpaces();

      expect(spaces).toHaveLength(1);
      expect(spaces[0].name).toBe('Space 1');
      expect(activeSpaceId).toBe(spaces[0].id);
    });

    it('should handle non-array data', () => {
      localStorage.setItem('wca.spaces.v1', JSON.stringify({ not: 'array' }));

      const { spaces } = safeLoadSpaces();

      expect(spaces).toHaveLength(1);
      expect(spaces[0].name).toBe('Space 1');
    });

    it('should add updatedAt if missing', () => {
      const space = createDefaultSpace();
      delete (space as any).updatedAt;

      localStorage.setItem('wca.spaces.v1', JSON.stringify([space]));

      const { spaces } = safeLoadSpaces();

      expect(spaces[0].updatedAt).toBeDefined();
    });
  });

  describe('persistSpaces', () => {
    it('should persist spaces to localStorage', (done) => {
      const space1 = createDefaultSpace('Space 1');
      const space2 = createDefaultSpace('Space 2');

      persistSpaces([space1, space2], space1.id, 10);

      setTimeout(() => {
        const stored = localStorage.getItem('wca.spaces.v1');
        const storedActiveId = localStorage.getItem('wca.activeSpaceId.v1');

        expect(stored).toBeDefined();
        expect(JSON.parse(stored!)).toHaveLength(2);
        expect(storedActiveId).toBe(space1.id);
        done();
      }, 50);
    });

    it('should debounce multiple calls', (done) => {
      const space = createDefaultSpace();
      let callCount = 0;

      const originalSetItem = localStorage.setItem;
      localStorage.setItem = jest.fn((key, value) => {
        if (key === 'wca.spaces.v1') callCount++;
        originalSetItem.call(localStorage, key, value);
      });

      persistSpaces([space], space.id, 50);
      persistSpaces([space], space.id, 50);
      persistSpaces([space], space.id, 50);

      setTimeout(() => {
        expect(callCount).toBe(1);
        localStorage.setItem = originalSetItem;
        done();
      }, 100);
    });

    it('should handle null activeSpaceId', (done) => {
      const space = createDefaultSpace();

      persistSpaces([space], null, 10);

      setTimeout(() => {
        const stored = localStorage.getItem('wca.spaces.v1');
        expect(stored).toBeDefined();
        done();
      }, 50);
    });

    it('should handle localStorage errors gracefully', (done) => {
      const space = createDefaultSpace();
      
      const originalSetItem = localStorage.setItem;
      localStorage.setItem = jest.fn(() => {
        throw new Error('Storage full');
      });

      expect(() => {
        persistSpaces([space], space.id, 10);
      }).not.toThrow();

      setTimeout(() => {
        localStorage.setItem = originalSetItem;
        done();
      }, 50);
    });
  });
});
