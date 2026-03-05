import SourcePreview from '../src/features/sources/ui/SourcePreview';
import AgentLog from '../src/features/logs/ui/AgentLog';
import InputTab from './InputTab';
import ResultsTab from './ResultsTab';
import EmailTab from './EmailTab';
import { TabContentProps } from './types';

export default function TabContent({ 
  activeTab, 
  activeSpace, 
  health, 
  onIngest, 
  onUpdateSource, 
  onInputChange,
  onCreateSpace 
}: TabContentProps) {
  const isFullHeight = ['log', 'email', 'results'].includes(activeTab);
  const containerStyle = isFullHeight ? { height: 'calc(100vh - 20rem)' } : {};
  const containerClass = isFullHeight ? '' : 'space-y-6';

  return (
    <div className={containerClass} style={containerStyle}>
      {activeTab === 'input' && (
        <InputTab
          activeSpace={activeSpace}
          health={health}
          onIngest={onIngest}
          onInputChange={onInputChange}
          onCreateSpace={onCreateSpace}
        />
      )}

      {activeTab === 'sources' && (
        <SourcePreview sources={activeSpace.sources.items} onUpdateSource={onUpdateSource} />
      )}

      {activeTab === 'results' && (
        <ResultsTab 
          analysis={activeSpace.results.analysis}
          reportMarkdown={activeSpace.results.reportMarkdown}
        />
      )}

      {activeTab === 'email' && (
        <EmailTab emailBody={activeSpace.email.body} />
      )}

      {activeTab === 'log' && (
        <AgentLog logs={activeSpace.log.entries} loading={activeSpace.loading} />
      )}
    </div>
  );
}
