import UrlInputForm from '../src/features/analysis/ui/UrlInputForm';
import { InputTabProps } from './types';

export default function InputTab({ activeSpace, health, onIngest, onInputChange, onCreateSpace }: InputTabProps) {
  if (activeSpace.results.analysis) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">Analysis Complete</h3>
          <p className="text-gray-600 mb-6">This space has finished its analysis. Create a new space to run another analysis.</p>
          <button
            onClick={onCreateSpace}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700"
          >
            + Create New Space
          </button>
        </div>
      </div>
    );
  }

  return (
    <UrlInputForm 
      onIngest={onIngest} 
      loading={activeSpace.loading || health.checking} 
      disabled={health.checking || !health.openaiConfigured}
      initialUrls={activeSpace.input.urls}
      initialText={activeSpace.input.pastedText}
      initialMode={activeSpace.input.analysisMode}
      initialTone={activeSpace.input.tone}
      onInputChange={onInputChange}
    />
  );
}
