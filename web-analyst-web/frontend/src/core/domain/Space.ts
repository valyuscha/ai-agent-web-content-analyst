import { Source } from './Source';

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
