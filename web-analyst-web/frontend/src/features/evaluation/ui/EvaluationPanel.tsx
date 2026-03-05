'use client';

import { useState } from 'react';

interface EvaluationPanelProps {
  resultJson: any;
  onEvaluate: (predicted: string[], gold?: string[], checkedIds?: number[]) => void;
  evaluationResult: any;
}

export default function EvaluationPanel({ resultJson, onEvaluate, evaluationResult }: EvaluationPanelProps) {
  const [method, setMethod] = useState<'checkbox' | 'gold'>('checkbox');
  const [goldList, setGoldList] = useState('');
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set());

  const allItems: string[] = [];
  resultJson?.sources?.forEach((source: any) => {
    source.action_items?.forEach((item: string) => {
      allItems.push(item);
    });
  });

  const handleCheckbox = (index: number) => {
    const newChecked = new Set(checkedItems);
    if (newChecked.has(index)) {
      newChecked.delete(index);
    } else {
      newChecked.add(index);
    }
    setCheckedItems(newChecked);
  };

  const handleEvaluate = () => {
    if (method === 'checkbox') {
      onEvaluate(allItems, undefined, Array.from(checkedItems));
    } else {
      const goldItems = goldList.split('\n').filter(line => line.trim());
      onEvaluate(allItems, goldItems);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">Evaluation</h2>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Evaluation Method</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              checked={method === 'checkbox'}
              onChange={() => setMethod('checkbox')}
              className="mr-2"
            />
            Checkbox-based
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              checked={method === 'gold'}
              onChange={() => setMethod('gold')}
              className="mr-2"
            />
            Gold List
          </label>
        </div>
      </div>

      {method === 'checkbox' ? (
        <div className="space-y-2 mb-4">
          <p className="text-sm text-gray-600 mb-2">Mark correct action items:</p>
          {allItems.map((item, index) => (
            <label key={index} className="flex items-start gap-2 p-2 hover:bg-gray-50 rounded">
              <input
                type="checkbox"
                checked={checkedItems.has(index)}
                onChange={() => handleCheckbox(index)}
                className="mt-1"
              />
              <span className="text-sm">{item}</span>
            </label>
          ))}
        </div>
      ) : (
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Gold Standard Action Items (one per line)</label>
          <textarea
            value={goldList}
            onChange={(e) => setGoldList(e.target.value)}
            className="w-full border rounded p-2 h-32 text-sm font-mono"
            placeholder="Enter gold standard action items..."
          />
        </div>
      )}

      <button
        onClick={handleEvaluate}
        disabled={allItems.length === 0}
        className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
      >
        Calculate Metrics
      </button>

      {evaluationResult && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-bold mb-3">Evaluation Results</h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-white p-3 rounded">
              <p className="text-sm text-gray-600">Precision</p>
              <p className="text-2xl font-bold">{(evaluationResult.precision * 100).toFixed(1)}%</p>
            </div>
            {evaluationResult.recall !== null && (
              <>
                <div className="bg-white p-3 rounded">
                  <p className="text-sm text-gray-600">Recall</p>
                  <p className="text-2xl font-bold">{(evaluationResult.recall * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-white p-3 rounded">
                  <p className="text-sm text-gray-600">F1 Score</p>
                  <p className="text-2xl font-bold">{(evaluationResult.f1 * 100).toFixed(1)}%</p>
                </div>
              </>
            )}
          </div>

          {evaluationResult.matching_details?.length > 0 && (
            <div>
              <p className="font-semibold text-sm mb-2">Matches:</p>
              <div className="space-y-2">
                {evaluationResult.matching_details.map((match: any, i: number) => (
                  <div key={i} className="bg-white p-2 rounded text-sm">
                    <p><span className="font-medium">Predicted:</span> {match.predicted}</p>
                    <p><span className="font-medium">Gold:</span> {match.gold}</p>
                    <p className="text-xs text-gray-600">Similarity: {match.similarity.toFixed(2)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
