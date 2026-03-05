import { useState, useEffect } from 'react';
import { apiClient } from '../infrastructure/apiClient';

export function useHealthCheck() {
  const [openaiConfigured, setOpenaiConfigured] = useState<boolean | null>(null);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      setChecking(true);
      try {
        const response = await apiClient.health();
        setOpenaiConfigured(response.openai_configured);
        setError(null);
      } catch (err) {
        console.error('Health check failed:', err);
        setOpenaiConfigured(false);
        setError('Cannot connect to backend server. Make sure it is running on http://localhost:8000');
      } finally {
        setChecking(false);
      }
    };
    
    checkHealth();
  }, []);

  return { openaiConfigured, checking, error };
}
