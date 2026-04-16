'use client';

import { useSpaces } from '../src/features/spaces/application/SpaceContext';
import { useAnalysisWorkflow } from '../src/core/application';
import SpaceSelector from '../src/features/spaces/ui/SpaceSelector';
import HealthStatus from '../src/shared/ui/HealthStatus';
import ErrorDisplay from '../src/shared/ui/ErrorDisplay';
import LoadingSpinner from '../src/shared/ui/LoadingSpinner';
import TabNavigation from '../src/shared/ui/TabNavigation';
import TabContent from './TabContent';
import { TABS } from './constants';

export default function Home() {
  const { activeSpace, dispatch } = useSpaces();
  const { health, ingest, updateSource, run, updateInput, updateTab } = useAnalysisWorkflow();

  if (!activeSpace) {
    return <LoadingSpinner />;
  }

  const isAnalysisComplete = !!activeSpace.results.analysis;
  const hasSession = !!activeSpace.results.sessionId;
  const canRunAnalysis = hasSession && !isAnalysisComplete && !activeSpace.loading;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-3 py-3 sm:px-4 sm:py-4">
          <div className="flex flex-wrap items-center gap-2 sm:gap-4 sm:justify-between">
            <div className="text-center sm:text-left w-full sm:w-auto">
              <h1 className="text-2xl sm:text-3xl font-bold whitespace-nowrap"><span>🤖 </span><span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Web Content Analyst</span></h1>
              <p className="text-gray-600 text-sm">AI-powered content analysis with RAG and self-reflection</p>
            </div>
            <div className="flex items-center justify-center gap-2 w-full sm:w-auto">
              <SpaceSelector />
              <HealthStatus checking={health.checking} configured={health.openaiConfigured} />
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-3 py-4 sm:px-4 sm:py-6">
        {!health.checking && health.openaiConfigured === false && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 font-semibold">⚠️ Server Configuration Required</p>
            <p className="text-red-700 text-sm mt-1">
              The server administrator needs to configure the OPENAI_API_KEY environment variable.
            </p>
          </div>
        )}

        {activeSpace.error && !activeSpace.loading && isAnalysisComplete && (
          <ErrorDisplay error={activeSpace.error} />
        )}

        {canRunAnalysis && (
          <div className="mb-6">
            <button
              onClick={run}
              disabled={health.checking || !health.openaiConfigured}
              className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400"
            >
              {health.checking ? 'Checking Server...' : '🚀 Run Agent Analysis'}
            </button>
          </div>
        )}

        <TabNavigation 
          tabs={TABS} 
          activeTab={activeSpace.ui.activeTab} 
          onTabChange={updateTab} 
        />

        <TabContent
          activeTab={activeSpace.ui.activeTab}
          activeSpace={activeSpace}
          health={health}
          onIngest={ingest}
          onUpdateSource={updateSource}
          onInputChange={updateInput}
          onCreateSpace={() => dispatch({ type: 'CREATE_SPACE' })}
        />
      </div>
    </div>
  );
}
