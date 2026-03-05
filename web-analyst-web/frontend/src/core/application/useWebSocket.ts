import { useCallback, useRef } from 'react';
import { apiClient } from '../infrastructure/apiClient';

interface WebSocketMessage {
  type: string;
  message?: string;
  detail?: any;
}

interface UseWebSocketOptions {
  onMessage: (data: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onClose?: () => void;
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback((sessionId: string, options: UseWebSocketOptions) => {
    return new Promise<WebSocket>((resolve, reject) => {
      const ws = new WebSocket(apiClient.getWebSocketUrl(sessionId));
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        resolve(ws);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        options.onMessage(data);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        options.onError?.(error);
        reject(error);
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        options.onClose?.();
        wsRef.current = null;
      };

      setTimeout(() => reject(new Error('WebSocket connection timeout')), 5000);
    });
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return { connect, disconnect };
}
