/**
 * Hook for WebSocket connection management
 */
import { useSpaces } from '../../features/spaces/application/SpaceContext';

export function useWebSocket() {
  const { dispatch } = useSpaces();

  const connectWebSocket = async (sessionId: string, initiatingSpaceId: string): Promise<WebSocket> => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    
    await new Promise<void>((resolve, reject) => {
      ws.onopen = () => resolve();
      ws.onerror = (error) => reject(error);
      setTimeout(() => reject(new Error('WebSocket connection timeout')), 5000);
    });

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') {
        const logEntry = data.detail 
          ? { message: data.message, detail: data.detail } 
          : data.message;
        
        dispatch({
          type: 'APPEND_LOG',
          payload: { id: initiatingSpaceId, entry: logEntry },
        });
      }
    };

    ws.onclose = () => console.log('WebSocket closed');

    return ws;
  };

  return { connectWebSocket };
}
