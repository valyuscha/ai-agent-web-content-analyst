/**
 * Facade hook combining all analysis workflows
 * @deprecated Use individual hooks (useIngest, useRunAnalysis, useReflect, useUpdateSource) instead
 */
import { useIngest } from './useIngest';
import { useUpdateSource } from './useUpdateSource';
import { useRunAnalysis } from './useRunAnalysis';
import { useReflect } from './useReflect';

export function useAnalysisWorkflow() {
  const { ingest } = useIngest();
  const { updateSource } = useUpdateSource();
  const { run } = useRunAnalysis();
  const { reflect } = useReflect();

  return {
    handleIngest: ingest,
    handleUpdateSource: updateSource,
    handleRun: run,
    handleReflect: reflect,
  };
}

