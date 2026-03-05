import { useCallback } from 'react';
import { apiClient } from '../infrastructure/apiClient';
import { useSpaces } from '../../features/spaces/application/SpaceContext';

export function useIngest() {
  const { activeSpace, captureInitiatingSpaceId, dispatch, updateActiveSpace } = useSpaces();

  const ingest = useCallback(async (urls: string[], mode: string, tone: string) => {
    const initiatingSpaceId = captureInitiatingSpaceId();
    if (!initiatingSpaceId || !activeSpace) return;

    updateActiveSpace({ loading: true, error: null });
    
    try {
      const response = await apiClient.ingest({
        urls,
        analysis_mode: mode,
        tone,
        language: 'English',
      });
      
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: {
            results: {
              ...activeSpace.results,
              sessionId: response.session_id,
            },
            sources: {
              items: response.sources,
            },
            ui: {
              ...activeSpace.ui,
              activeTab: 'sources',
            },
            loading: false,
          },
        },
      });
    } catch (err: any) {
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: { error: err.message, loading: false },
        },
      });
    }
  }, [activeSpace, captureInitiatingSpaceId, dispatch, updateActiveSpace]);

  return { ingest };
}
