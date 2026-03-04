import { Space } from '../domain/Space';
import { createDefaultSpace } from '../domain/spaceFactory';

const STORAGE_VERSION = 'v1';
const SPACES_KEY = `wca.spaces.${STORAGE_VERSION}`;
const ACTIVE_SPACE_KEY = `wca.activeSpaceId.${STORAGE_VERSION}`;

export function safeLoadSpaces(): { spaces: Space[]; activeSpaceId: string | null } {
  try {
    const spacesJson = localStorage.getItem(SPACES_KEY);
    const activeId = localStorage.getItem(ACTIVE_SPACE_KEY);

    if (spacesJson) {
      const spaces = JSON.parse(spacesJson) as Space[];
      
      if (Array.isArray(spaces) && spaces.length > 0) {
        const validSpaces = spaces.map(s => ({
          ...createDefaultSpace(),
          ...s,
          error: s.results?.sessionId ? s.error : null,
          results: {
            ...s.results,
            sessionId: s.results?.analysis ? s.results.sessionId : null,
          },
          updatedAt: s.updatedAt || s.createdAt || Date.now(),
        }));
        
        const validActiveId = activeId && validSpaces.some(s => s.id === activeId) 
          ? activeId 
          : validSpaces[0].id;
        
        return { spaces: validSpaces, activeSpaceId: validActiveId };
      }
    }
  } catch (err) {
    console.error('Failed to load spaces from localStorage:', err);
  }

  const defaultSpace = createDefaultSpace('Space 1', 1);
  return { spaces: [defaultSpace], activeSpaceId: defaultSpace.id };
}

let persistTimeout: NodeJS.Timeout | null = null;

export function persistSpaces(spaces: Space[], activeSpaceId: string | null, debounceMs = 300) {
  if (persistTimeout) {
    clearTimeout(persistTimeout);
  }

  persistTimeout = setTimeout(() => {
    try {
      localStorage.setItem(SPACES_KEY, JSON.stringify(spaces));
      if (activeSpaceId) {
        localStorage.setItem(ACTIVE_SPACE_KEY, activeSpaceId);
      }
    } catch (err) {
      console.error('Failed to persist spaces to localStorage:', err);
    }
  }, debounceMs);
}
