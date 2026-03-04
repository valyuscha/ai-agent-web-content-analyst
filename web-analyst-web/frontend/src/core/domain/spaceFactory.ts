import { Space } from '../domain/Space';

export function createDefaultSpace(name?: string, index?: number): Space {
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

export function deepCloneSpace(space: Space, newName?: string): Space {
  const cloned = JSON.parse(JSON.stringify(space));
  cloned.id = `space-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  cloned.name = newName || `Copy of ${space.name}`;
  cloned.createdAt = Date.now();
  cloned.updatedAt = Date.now();
  return cloned;
}
