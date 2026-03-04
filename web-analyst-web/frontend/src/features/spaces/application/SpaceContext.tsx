'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { safeLoadSpaces, persistSpaces } from '../../../core/infrastructure/spaceStorage';
import { migrateOldBlocks } from '../../../core/infrastructure/spaceMigration';
import { spaceReducer } from './spaceReducer';

export interface Source {
  id?: string;
  url?: string;
  title?: string;
  type?: string;
  content?: string;
  extractedText?: string;
  metadata?: any;
  addedAt?: number;
  status?: string;
  error?: string | null;
  text_preview?: string;
  text_length?: number;
}

export interface Space {
  id: string;
  name: string;
  createdAt: number;
  updatedAt: number;
  input: {
    urls: string[];
    pastedText: string;
    analysisMode: string;
    tone: string;
  };
  sources: {
    items: Source[];
  };
  results: {
    sessionId: string | null;
    analysis: any;
    structuredData: any;
    reportMarkdown: string;
    metrics: any;
  };
  email: {
    subject: string;
    body: string;
    recipients?: string[];
  };
  log: {
    entries: Array<string | { message: string; detail?: string }>;
  };
  ui: {
    activeTab: 'input' | 'sources' | 'results' | 'email' | 'log';
  };
  loading: boolean;
  error: string | null;
}

export interface SpaceState {
  spaces: Space[];
  activeSpaceId: string | null;
}

export type SpaceAction =
  | { type: 'SET_SPACES'; payload: Space[] }
  | { type: 'SET_ACTIVE_SPACE'; payload: string | null }
  | { type: 'CREATE_SPACE'; payload?: string }
  | { type: 'DELETE_SPACE'; payload: string }
  | { type: 'RENAME_SPACE'; payload: { id: string; name: string } }
  | { type: 'DUPLICATE_SPACE'; payload: string }
  | { type: 'UPDATE_SPACE'; payload: { id: string; updates: Partial<Space> } }
  | { type: 'APPEND_LOG'; payload: { id: string; entry: string | { message: string; detail?: string } } }
  | { type: 'RESET_SPACE'; payload: string };

const SpaceContext = createContext<{
  state: SpaceState;
  dispatch: React.Dispatch<SpaceAction>;
  activeSpace: Space | null;
  updateActiveSpace: (updates: Partial<Space>) => void;
  captureInitiatingSpaceId: () => string | null;
} | null>(null);

export function SpaceProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(spaceReducer, { spaces: [], activeSpaceId: null });

  useEffect(() => {
    const migrated = migrateOldBlocks();
    if (migrated && migrated.length > 0) {
      dispatch({ type: 'SET_SPACES', payload: migrated });
      dispatch({ type: 'SET_ACTIVE_SPACE', payload: migrated[0].id });
    } else {
      const { spaces, activeSpaceId } = safeLoadSpaces();
      dispatch({ type: 'SET_SPACES', payload: spaces });
      dispatch({ type: 'SET_ACTIVE_SPACE', payload: activeSpaceId });
    }
  }, []);

  useEffect(() => {
    if (state.spaces.length > 0) {
      persistSpaces(state.spaces, state.activeSpaceId);
    }
  }, [state.spaces, state.activeSpaceId]);

  const activeSpace = state.spaces.find(s => s.id === state.activeSpaceId) || null;

  const updateActiveSpace = (updates: Partial<Space>) => {
    if (state.activeSpaceId) {
      dispatch({
        type: 'UPDATE_SPACE',
        payload: { id: state.activeSpaceId, updates },
      });
    }
  };

  const captureInitiatingSpaceId = () => state.activeSpaceId;

  return (
    <SpaceContext.Provider value={{ state, dispatch, activeSpace, updateActiveSpace, captureInitiatingSpaceId }}>
      {children}
    </SpaceContext.Provider>
  );
}

export function useSpaces() {
  const context = useContext(SpaceContext);
  if (!context) {
    throw new Error('useSpaces must be used within SpaceProvider');
  }
  return context;
}
