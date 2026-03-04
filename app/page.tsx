'use client';

import { useState, useEffect } from 'react';

type AnalysisBlock = {
  id: string;
  urls: string[];
  textContent: string;
  analysis: string;
  createdAt: number;
};

export default function Home() {
  const [blocks, setBlocks] = useState<AnalysisBlock[]>([]);
  const [currentBlock, setCurrentBlock] = useState({ urls: '', textContent: '', analysis: '' });

  useEffect(() => {
    const saved = localStorage.getItem('analysisBlocks');
    if (saved) setBlocks(JSON.parse(saved));
  }, []);

  const saveBlock = () => {
    const newBlock: AnalysisBlock = {
      id: Date.now().toString(),
      urls: currentBlock.urls.split('\n').filter(u => u.trim()),
      textContent: currentBlock.textContent,
      analysis: currentBlock.analysis,
      createdAt: Date.now(),
    };
    const updated = [...blocks, newBlock];
    setBlocks(updated);
    localStorage.setItem('analysisBlocks', JSON.stringify(updated));
    setCurrentBlock({ urls: '', textContent: '', analysis: '' });
  };

  const deleteBlock = (id: string) => {
    const updated = blocks.filter(b => b.id !== id);
    setBlocks(updated);
    localStorage.setItem('analysisBlocks', JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 dark:text-white">Analysis Blocks</h1>
        
        <div className="bg-white dark:bg-zinc-900 p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Create New Block</h2>
          <textarea
            placeholder="URLs (one per line)"
            value={currentBlock.urls}
            onChange={(e) => setCurrentBlock({ ...currentBlock, urls: e.target.value })}
            className="w-full p-2 border rounded mb-4 dark:bg-zinc-800 dark:text-white"
            rows={3}
          />
          <textarea
            placeholder="Text content"
            value={currentBlock.textContent}
            onChange={(e) => setCurrentBlock({ ...currentBlock, textContent: e.target.value })}
            className="w-full p-2 border rounded mb-4 dark:bg-zinc-800 dark:text-white"
            rows={4}
          />
          <textarea
            placeholder="Analysis"
            value={currentBlock.analysis}
            onChange={(e) => setCurrentBlock({ ...currentBlock, analysis: e.target.value })}
            className="w-full p-2 border rounded mb-4 dark:bg-zinc-800 dark:text-white"
            rows={4}
          />
          <button
            onClick={saveBlock}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Save Block
          </button>
        </div>

        <div className="space-y-4">
          {blocks.map((block) => (
            <div key={block.id} className="bg-white dark:bg-zinc-900 p-6 rounded-lg shadow">
              <div className="flex justify-between items-start mb-4">
                <span className="text-sm text-zinc-500">
                  {new Date(block.createdAt).toLocaleString()}
                </span>
                <button
                  onClick={() => deleteBlock(block.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  Delete
                </button>
              </div>
              {block.urls.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-semibold dark:text-white mb-2">Sources:</h3>
                  {block.urls.map((url, i) => (
                    <a key={i} href={url} className="text-blue-600 block text-sm" target="_blank">
                      {url}
                    </a>
                  ))}
                </div>
              )}
              {block.textContent && (
                <div className="mb-4">
                  <h3 className="font-semibold dark:text-white mb-2">Content:</h3>
                  <p className="text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">{block.textContent}</p>
                </div>
              )}
              {block.analysis && (
                <div>
                  <h3 className="font-semibold dark:text-white mb-2">Analysis:</h3>
                  <p className="text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">{block.analysis}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
