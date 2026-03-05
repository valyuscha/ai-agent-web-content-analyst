import { useCallback } from 'react';
import { apiClient } from '../infrastructure/apiClient';
import { useSpaces } from '../../features/spaces/application/SpaceContext';

export function useUpdateSource() {
  const { activeSpace, updateActiveSpace } = useSpaces();

  const updateSource = useCallback(async (url: string, text: string) => {
    if (!activeSpace?.results.sessionId) return;
    
    updateActiveSpace({ loading: true });
    
    try {
      await apiClient.updateSource(activeSpace.results.sessionId, url, text);
      updateActiveSpace({
        sources: {
          items: activeSpace.sources.items.map(s => 
            s.url === url 
              ? { ...s, status: 'ok', error: null, text_preview: text.substring(0, 500), text_length: text.length } 
              : s
          ),
        },
        loading: false,
      });
    } catch (err: any) {
      updateActiveSpace({ error: err.message, loading: false });
    }
  }, [activeSpace, updateActiveSpace]);

  return { updateSource };
}
