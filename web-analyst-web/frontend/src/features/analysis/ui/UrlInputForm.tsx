'use client';

import { useState, useEffect } from 'react';

interface UrlInputFormProps {
  onIngest: (urls: string[], mode: string, tone: string) => void;
  loading: boolean;
  disabled?: boolean;
  initialUrls?: string[];
  initialText?: string;
  initialMode?: string;
  initialTone?: string;
  onInputChange?: (urls: string[], text: string, mode: string, tone: string) => void;
}

export default function UrlInputForm({ 
  onIngest, 
  loading, 
  disabled,
  initialUrls = [''],
  initialText = '',
  initialMode = 'General summary',
  initialTone = 'formal',
  onInputChange
}: UrlInputFormProps) {
  const [urlInputs, setUrlInputs] = useState<string[]>(initialUrls);
  const [textContext, setTextContext] = useState(initialText);
  const [mode, setMode] = useState(initialMode);
  const [tone, setTone] = useState(initialTone);
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  useEffect(() => {
    setUrlInputs(initialUrls);
    setTextContext(initialText);
    setMode(initialMode);
    setTone(initialTone);
  }, [initialUrls, initialText, initialMode, initialTone]);

  useEffect(() => {
    if (onInputChange) {
      onInputChange(urlInputs, textContext, mode, tone);
    }
  }, [urlInputs, textContext, mode, tone]);

  const isValidUrl = (str: string) => {
    try {
      new URL(str);
      return true;
    } catch {
      return false;
    }
  };

  const addUrlInput = () => {
    setUrlInputs([...urlInputs, '']);
  };

  const removeUrlInput = (index: number) => {
    if (urlInputs.length > 1) {
      setUrlInputs(urlInputs.filter((_, i) => i !== index));
      const newErrors = {...errors};
      delete newErrors[`url-${index}`];
      setErrors(newErrors);
    }
  };

  const updateUrlInput = (index: number, value: string) => {
    const newUrls = [...urlInputs];
    newUrls[index] = value;
    setUrlInputs(newUrls);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: {[key: string]: string} = {};

    const validUrls: string[] = [];
    urlInputs.forEach((url, index) => {
      if (url.trim()) {
        if (!isValidUrl(url.trim())) {
          newErrors[`url-${index}`] = 'Invalid URL format';
        } else {
          validUrls.push(url.trim());
        }
      }
    });

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0 && validUrls.length > 0) {
      onIngest(validUrls, mode, tone);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">Input Configuration</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Article URLs</label>
          <div className="space-y-2">
            {urlInputs.map((url, index) => (
              <div key={index} className="flex gap-2">
                <div className="flex-1">
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => updateUrlInput(index, e.target.value)}
                    className={`w-full border rounded-lg p-3 ${errors[`url-${index}`] ? 'border-red-500' : ''}`}
                    placeholder="https://example.com/article"
                    disabled={loading}
                  />
                  {errors[`url-${index}`] && (
                    <p className="text-red-500 text-sm mt-1">{errors[`url-${index}`]}</p>
                  )}
                </div>
                {urlInputs.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeUrlInput(index)}
                    className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                    disabled={loading}
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={addUrlInput}
            className="mt-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
            disabled={loading}
          >
            + Add another link
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Analysis Mode</label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="w-full border rounded-lg p-2"
              disabled={loading}
            >
              <option>General summary</option>
              <option>Study notes</option>
              <option>Product/marketing analysis</option>
              <option>Technical tutorial extraction</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Tone</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full border rounded-lg p-2"
              disabled={loading}
            >
              <option value="formal">Formal</option>
              <option value="friendly">Friendly</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || disabled || urlInputs.every(u => !u.trim())}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : disabled ? 'Server Not Configured' : 'Ingest URLs'}
        </button>
      </form>
    </div>
  );
}
