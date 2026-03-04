'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { apiClient } from '../src/core/infrastructure/apiClient';
import { useSpaces } from '../src/features/spaces/application/SpaceContext';
import UrlInputForm from '../src/features/analysis/ui/UrlInputForm';
import SourcePreview from '../src/features/sources/ui/SourcePreview';
import ResultsView from '../src/features/analysis/ui/ResultsView';
import AgentLog from '../src/features/logs/ui/AgentLog';
import DownloadButtons from '../src/features/evaluation/ui/DownloadButtons';
import SpaceSelector from '../src/features/spaces/ui/SpaceSelector';

export default function Home() {
  const { activeSpace, updateActiveSpace, captureInitiatingSpaceId, dispatch } = useSpaces();
  const [openaiConfigured, setOpenaiConfigured] = useState<boolean | null>(null);
  const [checkingHealth, setCheckingHealth] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      setCheckingHealth(true);
      try {
        const response = await apiClient.health();
        setOpenaiConfigured(response.openai_configured);
      } catch (err) {
        console.error('Health check failed:', err);
        setOpenaiConfigured(false);
        if (activeSpace) {
          updateActiveSpace({ 
            error: 'Cannot connect to backend server. Make sure it is running on http://localhost:8000' 
          });
        }
      } finally {
        setCheckingHealth(false);
      }
    };
    
    checkHealth();
  }, []);

  const handleIngest = async (urls: string[], mode: string, tone: string) => {
    const initiatingSpaceId = captureInitiatingSpaceId();
    if (!initiatingSpaceId || !activeSpace) return;

    updateActiveSpace({ loading: true, error: null });
    
    try {
      const response = await apiClient.ingest({
        urls,
        analysis_mode: mode,
        tone,
        language: 'English',
      });
      
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: {
            results: {
              ...activeSpace.results,
              sessionId: response.session_id,
            },
            sources: {
              items: response.sources,
            },
            ui: {
              ...activeSpace.ui,
              activeTab: 'sources',
            },
            loading: false,
          },
        },
      });
    } catch (err: any) {
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: { error: err.message, loading: false },
        },
      });
    }
  };

  const handleUpdateSource = async (url: string, text: string) => {
    if (!activeSpace?.results.sessionId) return;
    
    updateActiveSpace({ loading: true });
    
    try {
      await apiClient.updateSource(activeSpace.results.sessionId, url, text);
      updateActiveSpace({
        sources: {
          items: activeSpace.sources.items.map(s => 
            s.url === url 
              ? { ...s, status: 'ok', error: null, text_preview: text.substring(0, 500), text_length: text.length } 
              : s
          ),
        },
        loading: false,
      });
    } catch (err: any) {
      updateActiveSpace({ error: err.message, loading: false });
    }
  };

  const handleRun = async () => {
    if (!activeSpace?.results.sessionId) return;
    
    const initiatingSpaceId = captureInitiatingSpaceId();
    if (!initiatingSpaceId) return;

    updateActiveSpace({ 
      loading: true, 
      error: null,
      ui: { ...activeSpace.ui, activeTab: 'log' },
      log: { entries: [] },
    });
    
    const ws = new WebSocket(`ws://localhost:8000/ws/${activeSpace.results.sessionId}`);
    
    try {
      await new Promise<void>((resolve, reject) => {
        ws.onopen = () => {
          console.log('WebSocket connected');
          resolve();
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
        
        setTimeout(() => reject(new Error('WebSocket connection timeout')), 5000);
      });
    } catch (err: any) {
      updateActiveSpace({ error: err.message, loading: false });
      return;
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') {
        const logEntry = data.detail ? { message: data.message, detail: data.detail } : data.message;
        
        dispatch({
          type: 'APPEND_LOG',
          payload: {
            id: initiatingSpaceId,
            entry: logEntry,
          },
        });
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket closed');
    };
    
    try {
      const response = await apiClient.run(activeSpace.results.sessionId);
      ws.close();
      
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: {
            results: {
              ...activeSpace.results,
              analysis: response.result_json,
              structuredData: response.result_json,
              reportMarkdown: response.report_markdown,
              metrics: response.metrics,
            },
            email: {
              ...activeSpace.email,
              body: response.email_draft,
            },
            log: {
              entries: response.agent_log,
            },
            loading: false,
          },
        },
      });
    } catch (err: any) {
      ws.close();
      dispatch({
        type: 'UPDATE_SPACE',
        payload: {
          id: initiatingSpaceId,
          updates: { error: err.message, loading: false },
        },
      });
    }
  };

  const handleInputChange = (urls: string[], text: string, mode: string, tone: string) => {
    updateActiveSpace({
      input: {
        urls,
        pastedText: text,
        analysisMode: mode,
        tone,
      },
    });
  };

  const handleTabChange = (tab: string) => {
    if (!activeSpace) return;
    updateActiveSpace({
      ui: {
        ...activeSpace.ui,
        activeTab: tab as any,
      },
    });
  };

  if (!activeSpace) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">Loading...</div>;
  }

  const tabs = [
    { id: 'input', label: '📝 Input' },
    { id: 'sources', label: '📄 Sources' },
    { id: 'results', label: '📊 Results' },
    { id: 'email', label: '📧 Email' },
    { id: 'log', label: '🔍 Log' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">🤖 Web Content Analyst</h1>
                <p className="text-gray-600 text-sm">AI-powered content analysis with RAG and self-reflection</p>
              </div>
              <SpaceSelector />
            </div>
            {checkingHealth ? (
              <div className="px-4 py-2 rounded-lg bg-blue-100 text-blue-800">
                <span className="animate-pulse">⏳ Checking Server...</span>
              </div>
            ) : openaiConfigured !== null && (
              <div className={`px-4 py-2 rounded-lg ${
                openaiConfigured ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {openaiConfigured ? '✓ OpenAI Configured' : '✗ OpenAI Not Configured'}
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {!checkingHealth && openaiConfigured === false && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 font-semibold">⚠️ Server Configuration Required</p>
            <p className="text-red-700 text-sm mt-1">
              The server administrator needs to configure the OPENAI_API_KEY environment variable.
            </p>
          </div>
        )}

        {activeSpace.error && activeSpace.loading === false && activeSpace.results.analysis && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">❌ {activeSpace.error}</p>
          </div>
        )}

        {activeSpace.results.sessionId && !activeSpace.results.analysis && !activeSpace.loading && (
          <div className="mb-6">
            <button
              onClick={handleRun}
              disabled={checkingHealth || !openaiConfigured}
              className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400"
            >
              {checkingHealth ? 'Checking Server...' : '🚀 Run Agent Analysis'}
            </button>
          </div>
        )}

        <div className="bg-white rounded-lg shadow mb-6">
          <div className="flex border-b overflow-x-auto">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`px-6 py-3 font-medium whitespace-nowrap focus:outline-none ${
                  activeSpace.ui.activeTab === tab.id
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className={activeSpace.ui.activeTab === 'log' || activeSpace.ui.activeTab === 'email' || activeSpace.ui.activeTab === 'results' ? '' : 'space-y-6'} style={activeSpace.ui.activeTab === 'log' || activeSpace.ui.activeTab === 'email' || activeSpace.ui.activeTab === 'results' ? { height: 'calc(100vh - 20rem)' } : {}}>
          {activeSpace.ui.activeTab === 'input' && (
            <>
              {activeSpace.results.analysis ? (
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">✅</div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">Analysis Complete</h3>
                    <p className="text-gray-600 mb-6">This space has finished its analysis. Create a new space to run another analysis.</p>
                    <button
                      onClick={() => dispatch({ type: 'CREATE_SPACE' })}
                      className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700"
                    >
                      + Create New Space
                    </button>
                  </div>
                </div>
              ) : (
                <UrlInputForm 
                  onIngest={handleIngest} 
                  loading={activeSpace.loading || checkingHealth} 
                  disabled={checkingHealth || !openaiConfigured}
                  initialUrls={activeSpace.input.urls}
                  initialText={activeSpace.input.pastedText}
                  initialMode={activeSpace.input.analysisMode}
                  initialTone={activeSpace.input.tone}
                  onInputChange={handleInputChange}
                />
              )}
            </>
          )}

          {activeSpace.ui.activeTab === 'sources' && (
            <SourcePreview sources={activeSpace.sources.items} onUpdateSource={handleUpdateSource} />
          )}

          {activeSpace.ui.activeTab === 'results' && activeSpace.results.analysis && (
            <div className="bg-white rounded-lg shadow-md p-6 flex flex-col h-full" style={{ height: 'calc(100vh - 16rem)' }}>
              <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
              <div className="flex-1 overflow-y-auto">
                <ResultsView reportMarkdown={activeSpace.results.reportMarkdown} resultJson={activeSpace.results.analysis} />
              </div>
            </div>
          )}

          {activeSpace.ui.activeTab === 'results' && !activeSpace.results.analysis && (
            <div className="bg-white rounded-lg shadow-md p-6 flex items-center justify-center" style={{ height: 'calc(100vh - 16rem)' }}>
              <div className="text-center text-gray-500">
                <p className="text-xl mb-2">📊</p>
                <p>No results yet. Run the agent to see analysis results.</p>
              </div>
            </div>
          )}

          {activeSpace.ui.activeTab === 'email' && activeSpace.email.body && (
            <div className="bg-white rounded-lg shadow-md p-6 flex flex-col h-full" style={{ height: 'calc(100vh - 16rem)' }}>
              <h2 className="text-2xl font-bold mb-4">Email Draft</h2>
              <div className="border rounded-lg p-4 flex-1 overflow-y-auto bg-gradient-to-br from-blue-50 to-indigo-50">
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
                  {activeSpace.email.body}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {activeSpace.ui.activeTab === 'email' && !activeSpace.email.body && (
            <div className="bg-white rounded-lg shadow-md p-6 flex items-center justify-center" style={{ height: 'calc(100vh - 16rem)' }}>
              <div className="text-center text-gray-500">
                <p className="text-xl mb-2">📧</p>
                <p>No email draft yet. Run the agent to generate an email.</p>
              </div>
            </div>
          )}

          {activeSpace.ui.activeTab === 'log' && (
            <AgentLog logs={activeSpace.log.entries} loading={activeSpace.loading} />
          )}
        </div>
      </div>
    </div>
  );
}
