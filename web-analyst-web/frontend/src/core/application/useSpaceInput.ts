import { useCallback } from 'react';
import { useSpaces } from '../../features/spaces/application/SpaceContext';

export function useSpaceInput() {
  const { activeSpace, updateActiveSpace } = useSpaces();

  const updateInput = useCallback((urls: string[], text: string, mode: string, tone: string) => {
    updateActiveSpace({
      input: {
        urls,
        pastedText: text,
        analysisMode: mode,
        tone,
      },
    });
  }, [updateActiveSpace]);

  const updateTab = useCallback((tab: string) => {
    if (!activeSpace) return;
    updateActiveSpace({
      ui: {
        ...activeSpace.ui,
        activeTab: tab as any,
      },
    });
  }, [activeSpace, updateActiveSpace]);

  return { updateInput, updateTab };
}
