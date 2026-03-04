import {
  HealthResponse,
  IngestRequest,
  IngestResponse,
  RunRequest,
  RunResponse,
  EvaluateRequest,
  EvaluateResponse,
} from '../../shared/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  },

  async ingest(data: IngestRequest): Promise<IngestResponse> {
    const response = await fetch(`${API_BASE_URL}/api/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ingest failed');
    }
    return response.json();
  },

  async updateSource(sessionId: string, url: string, manualText: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/update-source`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, url, manual_text: manualText }),
    });
    if (!response.ok) throw new Error('Update source failed');
  },

  async run(sessionId: string): Promise<RunResponse> {
    const response = await fetch(`${API_BASE_URL}/api/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Run failed');
    }
    return response.json();
  },

  async reflect(sessionId: string, onlyLowConfidence: boolean = true): Promise<RunResponse> {
    const response = await fetch(`${API_BASE_URL}/api/reflect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, only_low_confidence: onlyLowConfidence }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Reflect failed');
    }
    return response.json();
  },

  async evaluate(data: EvaluateRequest): Promise<EvaluateResponse> {
    const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Evaluate failed');
    return response.json();
  },

  getExportUrl(sessionId: string, format: 'md' | 'json'): string {
    return `${API_BASE_URL}/api/export?session_id=${sessionId}&format=${format}`;
  },

  async getSessionLog(sessionId: string): Promise<{ agent_log: string[] }> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/log`);
    if (!response.ok) throw new Error('Failed to fetch log');
    return response.json();
  },
};
