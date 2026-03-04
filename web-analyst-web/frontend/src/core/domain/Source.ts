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
