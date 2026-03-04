'use client';

import { useState } from 'react';
import { Source } from '../../spaces/application/SpaceContext';

interface SourcePreviewProps {
  sources: Source[];
  onUpdateSource: (url: string, text: string) => void;
}

export default function SourcePreview({ sources, onUpdateSource }: SourcePreviewProps) {
  const [manualTexts, setManualTexts] = useState<{ [key: string]: string }>({});

  const handleSave = (url: string) => {
    const text = manualTexts[url];
    if (text) {
      onUpdateSource(url, text);
      setManualTexts({ ...manualTexts, [url]: '' });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Sources Preview</h2>
      
      {sources.length === 0 ? (
        <p className="text-gray-500">No sources loaded yet.</p>
      ) : (
        <div className="space-y-3">
          {sources.map((source, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-semibold">{source.title || 'Untitled'}</span>
                <span className={`px-2 py-1 text-xs rounded ${
                  source.status === 'ok' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {source.status || 'unknown'}
                </span>
                <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                  {source.type || 'unknown'}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{source.url || ''}</p>

              {source.error && (
                <div>
                  <div className="bg-red-50 border border-red-200 rounded p-3 mb-3">
                    <p className="text-red-800 text-sm">❌ {source.error}</p>
                  </div>
                  <label className="block text-sm font-medium mb-2">Paste content manually:</label>
                  <textarea
                    value={manualTexts[source.url || ''] || ''}
                    onChange={(e) => setManualTexts({ ...manualTexts, [source.url || '']: e.target.value })}
                    className="w-full border rounded p-2 h-32 text-sm font-mono"
                    placeholder="Paste transcript or article text here..."
                  />
                  <button
                    onClick={() => handleSave(source.url || '')}
                    className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    Save Manual Content
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
