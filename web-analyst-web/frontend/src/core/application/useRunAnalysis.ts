/**
 * Hook for running analysis with WebSocket logging
 */
import { apiClient } from '../infrastructure/apiClient';
import { useSpaces } from '../../features/spaces/application/SpaceContext';
import { useWebSocket } from './useWebSocket';

export function useRunAnalysis() {
  const { activeSpace, updateActiveSpace, captureInitiatingSpaceId, dispatch } = useSpaces();
  const { connectWebSocket } = useWebSocket();

  const runAnalysis = async () => {
    if (!activeSpace?.results.sessionId) return;
    
    const initiatingSpaceId = captureInitiatingSpaceId();
    if (!initiatingSpaceId) return;

    updateActiveSpace({ 
      loading: true, 
      error: null,
      ui: { ...activeSpace.ui, activeTab: 'log' },
      log: { entries: [] },
    });
    
    let ws: WebSocket | null = null;
    
    try {
      ws = await connectWebSocket(activeSpace.results.sessionId, initiatingSpaceId);
    } catch (err: any) {
      updateActiveSpace({ error: err.message, loading: false });
      return;
    }
    
    try {
      const response = await apiClient.run(activeSpace.results.sessionId);
      ws.close();
      
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: {
            results: {
              ...activeSpace.results,
              analysis: response.result_json,
              structuredData: response.result_json,
              reportMarkdown: response.report_markdown,
              metrics: response.metrics,
            },
            email: {
              ...activeSpace.email,
              body: response.email_draft,
            },
            log: { entries: response.agent_log },
            loading: false,
          },
        },
      });
    } catch (err: any) {
      ws?.close();
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: { error: err.message, loading: false },
        },
      });
    }
  };

  return { runAnalysis };
}
