'use client';

import ReactMarkdown from 'react-markdown';
import { useState } from 'react';

interface ResultsViewProps {
  reportMarkdown: string;
  resultJson: any;
}

export default function ResultsView({ reportMarkdown, resultJson }: ResultsViewProps) {
  const [expandedSource, setExpandedSource] = useState<number | null>(null);

  return (
    <>      
      <div className="max-w-none mb-8 bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-100">
        <ReactMarkdown
          components={{
            h1: ({node, ...props}) => <h1 className="text-3xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-blue-300" {...props} />,
            h2: ({node, ...props}) => <h2 className="text-2xl font-bold text-gray-800 mt-6 mb-3 pb-2 border-b border-gray-300" {...props} />,
            h3: ({node, ...props}) => <h3 className="text-xl font-semibold text-gray-800 mt-4 mb-2" {...props} />,
            h4: ({node, ...props}) => <h4 className="text-lg font-semibold text-gray-700 mt-3 mb-2" {...props} />,
            p: ({node, ...props}) => <p className="text-gray-700 text-base leading-relaxed mb-4" {...props} />,
            ul: ({node, ...props}) => <ul className="space-y-2 my-4 ml-6 list-disc marker:text-blue-600" {...props} />,
            ol: ({node, ...props}) => <ol className="space-y-2 my-4 ml-6 list-decimal marker:text-blue-600" {...props} />,
            li: ({node, children, ...props}) => {
              const text = children?.toString() || '';
              const startsWithEmoji = text.length > 0 && text.charCodeAt(0) > 127;
              return <li className={`text-gray-700 leading-relaxed pl-2 ${startsWithEmoji ? 'list-none -ml-6' : ''}`} {...props}>{children}</li>;
            },
            strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
            em: ({node, ...props}) => <em className="italic text-gray-800" {...props} />,
          }}
        >
          {reportMarkdown}
        </ReactMarkdown>
      </div>

      {resultJson?.sources && (
        <div className="mt-8">
          <h3 className="text-xl font-bold mb-4 text-gray-800">Per-Source Details</h3>
          <div className="space-y-4">
            {resultJson.sources.map((source: any, index: number) => (
              <div key={index} className="border-2 border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 transition-colors">
                <div
                  className="p-4 cursor-pointer bg-gradient-to-r from-gray-50 to-gray-100 hover:from-blue-50 hover:to-indigo-50 flex items-center justify-between transition-colors"
                  onClick={() => setExpandedSource(expandedSource === index ? null : index)}
                >
                  <span className="font-semibold text-gray-800">{source.title}</span>
                  <span className="text-blue-500 text-xl">{expandedSource === index ? '▼' : '▶'}</span>
                </div>

                {expandedSource === index && (
                  <div className="p-6 bg-gray-50 space-y-5">
                    <div className="bg-white p-4 rounded-lg border-l-4 border-blue-500">
                      <p className="font-semibold text-sm text-blue-700 mb-2">Summary</p>
                      <div className="text-sm text-gray-700 prose prose-sm max-w-none">
                        <ReactMarkdown>{source.summary}</ReactMarkdown>
                      </div>
                    </div>

                    {source.key_points?.length > 0 && (
                      <div className="bg-white p-4 rounded-lg border-l-4 border-green-500">
                        <p className="font-semibold text-sm text-green-700 mb-3">Key Points</p>
                        <ul className="space-y-2">
                          {source.key_points.map((point: string, i: number) => (
                            <li key={i} className="flex items-start">
                              <span className="text-green-500 mr-2 mt-1">●</span>
                              <div className="text-sm text-gray-700 prose prose-sm max-w-none flex-1">
                                <ReactMarkdown>{point}</ReactMarkdown>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {source.action_items?.length > 0 && (
                      <div className="bg-white p-4 rounded-lg border-l-4 border-purple-500">
                        <p className="font-semibold text-sm text-purple-700 mb-3">Action Items</p>
                        <ul className="space-y-3">
                          {source.action_items.map((item: any, i: number) => (
                            <li key={i} className="bg-gradient-to-r from-purple-50 to-pink-50 p-3 rounded-lg border border-purple-200">
                              <div className="font-medium text-sm prose prose-sm max-w-none mb-2">
                                <ReactMarkdown>{item.task}</ReactMarkdown>
                              </div>
                              <div className="flex flex-wrap gap-2 text-xs">
                                <span className="bg-white px-2 py-1 rounded border border-gray-300">
                                  👤 {item.owner}
                                </span>
                                <span className="bg-white px-2 py-1 rounded border border-gray-300">
                                  📅 {item.due_date}
                                </span>
                                <span className={`px-2 py-1 rounded font-semibold ${
                                  item.priority === 'high' ? 'bg-red-100 text-red-700' :
                                  item.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                  'bg-green-100 text-green-700'
                                }`}>
                                  {item.priority.toUpperCase()}
                                </span>
                                <span className="bg-white px-2 py-1 rounded border border-gray-300">
                                  ✓ {(item.confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                              {item.source_quote && (
                                <p className="text-xs text-gray-600 italic mt-2 pl-3 border-l-2 border-gray-300">
                                  "{item.source_quote}"
                                </p>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
