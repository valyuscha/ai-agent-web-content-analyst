/**
 * Custom hook for backend health check
 */
import { useState, useEffect } from 'react';
import { apiClient } from '../infrastructure/apiClient';

export function useHealthCheck() {
  const [openaiConfigured, setOpenaiConfigured] = useState<boolean | null>(null);
  const [checkingHealth, setCheckingHealth] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      setCheckingHealth(true);
      try {
        const response = await apiClient.health();
        setOpenaiConfigured(response.openai_configured);
      } catch (err) {
        console.error('Health check failed:', err);
        setOpenaiConfigured(false);
      } finally {
        setCheckingHealth(false);
      }
    };
    
    checkHealth();
  }, []);

  return { openaiConfigured, checkingHealth };
}
