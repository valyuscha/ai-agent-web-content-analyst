/**
 * Space reducer - handles all space state mutations
 */
import { Space, SpaceState, SpaceAction } from './SpaceContext';

function createDefaultSpace(name?: string, index?: number): Space {
  const id = `space-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  const now = Date.now();
  
  return {
    id,
    name: name || `Space ${index || 1}`,
    createdAt: now,
    updatedAt: now,
    input: {
      urls: [''],
      pastedText: '',
      analysisMode: 'General summary',
      tone: 'formal',
    },
    sources: {
      items: [],
    },
    results: {
      sessionId: null,
      analysis: null,
      structuredData: null,
      reportMarkdown: '',
      metrics: null,
    },
    email: {
      subject: '',
      body: '',
      recipients: [],
    },
    log: {
      entries: [],
    },
    ui: {
      activeTab: 'input',
    },
    loading: false,
    error: null,
  };
}

function deepCloneSpace(space: Space, newName?: string): Space {
  const cloned = JSON.parse(JSON.stringify(space));
  cloned.id = `space-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  cloned.name = newName || `Copy of ${space.name}`;
  cloned.createdAt = Date.now();
  cloned.updatedAt = Date.now();
  return cloned;
}

export function spaceReducer(state: SpaceState, action: SpaceAction): SpaceState {
  switch (action.type) {
    case 'SET_SPACES':
      return { ...state, spaces: action.payload };

    case 'SET_ACTIVE_SPACE':
      return { ...state, activeSpaceId: action.payload };

    case 'CREATE_SPACE': {
      const newSpace = createDefaultSpace(action.payload, state.spaces.length + 1);
      return {
        ...state,
        spaces: [...state.spaces, newSpace],
        activeSpaceId: newSpace.id,
      };
    }

    case 'DELETE_SPACE': {
      const filtered = state.spaces.filter(s => s.id !== action.payload);
      
      if (filtered.length === 0) {
        const newSpace = createDefaultSpace('Space 1', 1);
        return {
          ...state,
          spaces: [newSpace],
          activeSpaceId: newSpace.id,
        };
      }
      
      const newActiveId = state.activeSpaceId === action.payload
        ? filtered[0].id
        : state.activeSpaceId;
      
      return {
        ...state,
        spaces: filtered,
        activeSpaceId: newActiveId,
      };
    }

    case 'RENAME_SPACE': {
      return {
        ...state,
        spaces: state.spaces.map(s =>
          s.id === action.payload.id
            ? { ...s, name: action.payload.name, updatedAt: Date.now() }
            : s
        ),
      };
    }

    case 'DUPLICATE_SPACE': {
      const original = state.spaces.find(s => s.id === action.payload);
      if (!original) return state;
      
      const duplicated = deepCloneSpace(original);
      return {
        ...state,
        spaces: [...state.spaces, duplicated],
        activeSpaceId: duplicated.id,
      };
    }

    case 'UPDATE_SPACE': {
      return {
        ...state,
        spaces: state.spaces.map(s =>
          s.id === action.payload.id
            ? { ...s, ...action.payload.updates, updatedAt: Date.now() }
            : s
        ),
      };
    }

    case 'APPEND_LOG': {
      return {
        ...state,
        spaces: state.spaces.map(s =>
          s.id === action.payload.id
            ? { 
                ...s, 
                log: { 
                  entries: [...s.log.entries, action.payload.entry] 
                },
                updatedAt: Date.now() 
              }
            : s
        ),
      };
    }

    case 'RESET_SPACE': {
      const space = state.spaces.find(s => s.id === action.payload);
      if (!space) return state;
      
      const resetSpace = createDefaultSpace(space.name);
      resetSpace.id = space.id;
      resetSpace.createdAt = space.createdAt;
      
      return {
        ...state,
        spaces: state.spaces.map(s => s.id === action.payload ? resetSpace : s),
      };
    }

    default:
      return state;
  }
}
