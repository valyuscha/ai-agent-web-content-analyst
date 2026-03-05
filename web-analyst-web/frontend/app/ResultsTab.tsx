import ResultsView from '../src/features/analysis/ui/ResultsView';
import { ResultsTabProps } from './types';

export default function ResultsTab({ analysis, reportMarkdown }: ResultsTabProps) {
  if (!analysis) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 flex items-center justify-center" style={{ height: 'calc(100vh - 16rem)' }}>
        <div className="text-center text-gray-500">
          <p className="text-xl mb-2">📊</p>
          <p>No results yet. Run the agent to see analysis results.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex flex-col h-full" style={{ height: 'calc(100vh - 16rem)' }}>
      <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">Analysis Results</h2>
      <div className="flex-1 overflow-y-auto">
        <ResultsView reportMarkdown={reportMarkdown} resultJson={analysis} />
      </div>
    </div>
  );
}
