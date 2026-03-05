import { ErrorDisplayProps } from './ErrorDisplay.types';

export default function ErrorDisplay({ error, onDismiss }: ErrorDisplayProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div className="flex items-start justify-between">
        <p className="text-red-800">❌ {error}</p>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-600 hover:text-red-800 ml-4"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
