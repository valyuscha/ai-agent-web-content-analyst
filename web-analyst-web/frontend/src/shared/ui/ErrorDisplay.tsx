/**
 * Error display component
 */
'use client';

interface ErrorDisplayProps {
  error: string | null;
}

export default function ErrorDisplay({ error }: ErrorDisplayProps) {
  if (!error) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p className="text-red-800 font-medium">Error:</p>
      <p className="text-red-700 text-sm mt-1">{error}</p>
    </div>
  );
}
