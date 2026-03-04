/**
 * Custom hook for managing space input state
 */
import { useSpaces } from '../../features/spaces/application/SpaceContext';

export function useSpaceInput() {
  const { activeSpace, updateActiveSpace } = useSpaces();

  const handleInputChange = (urls: string[], text: string, mode: string, tone: string) => {
    if (!activeSpace) return;
    
    updateActiveSpace({
      input: {
        urls,
        pastedText: text,
        analysisMode: mode,
        tone,
      },
    });
  };

  return { handleInputChange };
}
