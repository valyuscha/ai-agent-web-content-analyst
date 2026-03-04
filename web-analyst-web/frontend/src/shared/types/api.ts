export interface HealthResponse {
  status: string;
  openai_configured: boolean;
}

export interface IngestRequest {
  urls: string[];
  analysis_mode: string;
  tone: string;
  language: string;
}

export interface IngestResponse {
  sources: Array<{
    url: string;
    title: string;
    type: string;
    status: string;
    error: string | null;
    text_preview: string;
    text_length: number;
  }>;
  session_id: string;
}

export interface RunRequest {
  session_id: string;
}

export interface RunResponse {
  result_json: any;
  report_markdown: string;
  email_draft: string;
  metrics: {
    citation_coverage: number;
    low_conf_rate: number;
  };
  agent_log: string[];
}

export interface EvaluateRequest {
  predicted_action_items: string[];
  gold_action_items?: string[];
  checked_correct_ids?: number[];
}

export interface EvaluateResponse {
  precision: number;
  recall: number | null;
  f1: number | null;
  matching_details: Array<{
    predicted: string;
    gold: string;
    similarity: number;
  }>;
  method: string;
}
