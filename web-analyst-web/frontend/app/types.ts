export interface Tab {
  id: string;
  label: string;
}

export interface TabContentProps {
  activeTab: string;
  activeSpace: any;
  health: any;
  onIngest: (urls: string[], mode: string, tone: string) => void;
  onUpdateSource: (url: string, text: string) => void;
  onInputChange: (urls: string[], text: string, mode: string, tone: string) => void;
  onCreateSpace: () => void;
}

export interface InputTabProps {
  activeSpace: any;
  health: any;
  onIngest: (urls: string[], mode: string, tone: string) => void;
  onInputChange: (urls: string[], text: string, mode: string, tone: string) => void;
  onCreateSpace: () => void;
}

export interface ResultsTabProps {
  analysis: any;
  reportMarkdown: string;
}

export interface EmailTabProps {
  emailBody: string;
}
