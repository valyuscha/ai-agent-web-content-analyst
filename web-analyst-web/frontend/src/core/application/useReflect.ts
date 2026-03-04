/**
 * Hook for self-reflection workflow
 */
import { apiClient } from '../infrastructure/apiClient';
import { useSpaces } from '../../features/spaces/application/SpaceContext';

export function useReflect() {
  const { activeSpace, updateActiveSpace, captureInitiatingSpaceId, dispatch } = useSpaces();

  const reflect = async (onlyLowConfidence: boolean = true) => {
    if (!activeSpace?.results.sessionId) return;
    
    const initiatingSpaceId = captureInitiatingSpaceId();
    if (!initiatingSpaceId) return;

    updateActiveSpace({ loading: true, error: null });
    
    try {
      const response = await apiClient.reflect(activeSpace.results.sessionId, onlyLowConfidence);
      
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
            log: { entries: response.agent_log },
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
  };

  return { reflect };
}
