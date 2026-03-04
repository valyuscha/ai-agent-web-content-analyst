import { Space } from '../domain/Space';

export function migrateOldBlocks(): Space[] | null {
  try {
    const oldBlocks = localStorage.getItem('analysisBlocks');
    if (!oldBlocks) return null;

    const blocks = JSON.parse(oldBlocks);
    if (!Array.isArray(blocks)) return null;

    const spaces: Space[] = blocks.map((block: any, index: number) => ({
      id: block.id || `space-${Date.now()}-${index}`,
      name: block.name || `Space ${index + 1}`,
      createdAt: block.createdAt || Date.now(),
      updatedAt: Date.now(),
      input: {
        urls: [''],
        pastedText: '',
        analysisMode: 'General summary',
        tone: 'formal',
      },
      sources: {
        items: block.sources || [],
      },
      results: {
        sessionId: block.sessionId || null,
        analysis: block.resultJson || null,
        structuredData: block.resultJson || null,
        reportMarkdown: block.reportMarkdown || '',
        metrics: block.metrics || null,
      },
      email: {
        subject: '',
        body: block.emailDraft || '',
        recipients: [],
      },
      log: {
        entries: block.agentLog || [],
      },
      ui: {
        activeTab: 'input',
      },
      loading: false,
      error: null,
    }));

    localStorage.removeItem('analysisBlocks');
    
    return spaces;
  } catch (err) {
    console.error('Failed to migrate old blocks:', err);
    return null;
  }
}
