/**
 * Application layer hooks - orchestrate business logic
 */

// Health check
export { useHealthCheck } from './useHealthCheck';

// Space input management
export { useSpaceInput } from './useSpaceInput';

// Analysis workflows (individual hooks)
export { useIngest } from './useIngest';
export { useUpdateSource } from './useUpdateSource';
export { useRunAnalysis } from './useRunAnalysis';
export { useReflect } from './useReflect';
export { useWebSocket } from './useWebSocket';

// Facade hook (backward compatibility)
export { useAnalysisWorkflow } from './useAnalysisWorkflow';
