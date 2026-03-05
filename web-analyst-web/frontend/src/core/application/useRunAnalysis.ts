import { useCallback } from 'react';
import { apiClient } from '../infrastructure/apiClient';
import { useSpaces } from '../../features/spaces/application/SpaceContext';
import { useWebSocket } from './useWebSocket';

export function useRunAnalysis() {
  const { activeSpace, captureInitiatingSpaceId, dispatch, updateActiveSpace } = useSpaces();
  const { connect, disconnect } = useWebSocket();

  const run = useCallback(async () => {
    if (!activeSpace?.results.sessionId) return;
    
    const initiatingSpaceId = captureInitiatingSpaceId();
    if (!initiatingSpaceId) return;

    updateActiveSpace({ 
      loading: true, 
      error: null,
      ui: { ...activeSpace.ui, activeTab: 'log' },
      log: { entries: [] },
    });
    
    try {
      const ws = await connect(activeSpace.results.sessionId, {
        onMessage: (data) => {
          if (data.type === 'log') {
            const logEntry = data.detail 
              ? { message: data.message || '', detail: data.detail } 
              : data.message || '';
            
            dispatch({
              type: 'APPEND_LOG',
              payload: {
                id: initiatingSpaceId,
                entry: logEntry,
              },
            });
          }
        },
        onError: (error) => {
          updateActiveSpace({ 
            error: 'WebSocket connection failed', 
            loading: false 
          });
        },
      });

      const response = await apiClient.run(activeSpace.results.sessionId);
      disconnect();
      
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
            log: {
              entries: response.agent_log,
            },
            loading: false,
          },
        },
      });
    } catch (err: any) {
      disconnect();
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: { error: err.message, loading: false },
        },
      });
    }
  }, [activeSpace, captureInitiatingSpaceId, dispatch, updateActiveSpace, connect, disconnect]);

  return { run };
}
