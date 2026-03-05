import { useHealthCheck } from './useHealthCheck';
import { useIngest } from './useIngest';
import { useUpdateSource } from './useUpdateSource';
import { useRunAnalysis } from './useRunAnalysis';
import { useWebSocket } from './useWebSocket';
import { useSpaceInput } from './useSpaceInput';

export function useAnalysisWorkflow() {
  const health = useHealthCheck();
  const { ingest } = useIngest();
  const { updateSource } = useUpdateSource();
  const { run } = useRunAnalysis();
  const { updateInput, updateTab } = useSpaceInput();

  return {
    health,
    ingest,
    updateSource,
    run,
    updateInput,
    updateTab,
  };
}

export {
  useHealthCheck,
  useIngest,
  useUpdateSource,
  useRunAnalysis,
  useWebSocket,
  useSpaceInput,
};
