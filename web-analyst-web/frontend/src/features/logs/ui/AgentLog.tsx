'use client';

import { useEffect, useRef, useState } from 'react';

interface LogEntry {
  message: string;
  detail?: string;
}

interface AgentLogProps {
  logs: (string | LogEntry)[];
  loading?: boolean;
}

const formatLogEntry = (log: string) => {
  // Check for different log types and format accordingly
  if (log.includes('=== PLAN:')) {
    const mode = log.replace('=== PLAN:', '').replace('===', '').trim();
    return { icon: '🎯', text: `Starting analysis: ${mode}`, bgClass: 'bg-blue-50 text-blue-800' };
  }
  if (log.includes('Processing') && log.includes('sources')) {
    return { icon: '📚', text: log, bgClass: 'bg-violet-50 text-violet-800' };
  }
  if (log.includes('=== BUILDING VECTOR STORE ===')) {
    return { icon: '🔨', text: 'Building knowledge base...', bgClass: 'bg-yellow-50 text-yellow-800' };
  }
  if (log.includes('Indexed') && log.includes('chunks')) {
    const match = log.match(/(\d+)/);
    return { icon: '✅', text: `Indexed ${match ? match[0] : ''} knowledge chunks`, bgClass: 'bg-green-50 text-green-800' };
  }
  if (log.includes('=== PROCESSING:')) {
    const title = log.replace('=== PROCESSING:', '').replace('===', '').trim();
    return { icon: '📄', text: `Analyzing: ${title}`, bgClass: 'bg-blue-50 text-blue-800' };
  }
  if (log.includes('Retrieved') && log.includes('contexts')) {
    return { icon: '🔍', text: log, bgClass: 'bg-violet-50 text-violet-800' };
  }
  if (log.includes('Extracting structured insights')) {
    return { icon: '💡', text: 'Extracting key insights...', bgClass: 'bg-yellow-50 text-yellow-800' };
  }
  if (log.includes('Reflecting on extraction quality')) {
    return { icon: '🤔', text: 'Reviewing and improving quality...', bgClass: 'bg-violet-50 text-violet-800' };
  }
  if (log.includes('=== COMBINING SOURCES ===')) {
    return { icon: '🔗', text: 'Combining insights from all sources...', bgClass: 'bg-green-50 text-green-800' };
  }
  if (log.includes('=== COMPLETE ===')) {
    return { icon: '🎉', text: 'Analysis complete!', bgClass: 'bg-green-50 text-green-800' };
  }
  if (log.includes('Skipping')) {
    return { icon: '⏭️', text: log, bgClass: 'bg-gray-50 text-gray-700' };
  }
  
  // Default formatting
  return { icon: '', text: log, bgClass: 'bg-gray-50 text-gray-800' };
};

export default function AgentLog({ logs, loading }: AgentLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const handleScroll = () => {
    if (scrollRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 10;
      setAutoScroll(isAtBottom);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex flex-col" style={{ height: 'calc(100vh - 16rem)' }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Agent Progress</h2>
        {loading && (
          <div className="flex items-center gap-2 text-blue-600">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-sm font-medium">Thinking...</span>
          </div>
        )}
      </div>
      
      <div ref={scrollRef} onScroll={handleScroll} className="space-y-3 overflow-y-auto flex-1 pr-2">
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">Waiting for analysis to start...</p>
          </div>
        ) : (
          logs.map((log, index) => {
            const message = typeof log === 'string' ? log : log.message;
            const detail = typeof log === 'object' ? log.detail : '';
            const formatted = formatLogEntry(message);
            const isExpanded = expandedIndex === index;
            const hasDetail = detail && detail.length > 0;
            
            return (
              <div key={index} className={`rounded-lg ${formatted.bgClass} border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 animate-fadeIn`}>
                <div 
                  className={`flex items-center gap-3 p-4 ${hasDetail ? 'cursor-pointer hover:bg-opacity-80' : ''}`}
                  onClick={() => hasDetail && setExpandedIndex(isExpanded ? null : index)}
                >
                  <span className="text-2xl flex-shrink-0">{formatted.icon}</span>
                  <span className="flex-1 font-medium text-sm">{formatted.text}</span>
                  {hasDetail && (
                    <span className="text-gray-400 text-sm transition-transform duration-200" style={{ transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)' }}>▶</span>
                  )}
                </div>
                {hasDetail && isExpanded && (
                  <div className="px-4 pb-4 pt-0 animate-fadeIn">
                    <div className="pl-9 text-sm text-gray-600 bg-white bg-opacity-70 p-3 rounded border-l-2 border-gray-300">
                      {detail}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
