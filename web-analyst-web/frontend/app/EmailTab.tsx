import ReactMarkdown from 'react-markdown';
import { MARKDOWN_COMPONENTS } from './markdownConfig';
import { EmailTabProps } from './types';

export default function EmailTab({ emailBody }: EmailTabProps) {
  if (!emailBody) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 flex items-center justify-center" style={{ height: 'calc(100vh - 16rem)' }}>
        <div className="text-center text-gray-500">
          <p className="text-xl mb-2">📧</p>
          <p>No email draft yet. Run the agent to generate an email.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex flex-col h-full" style={{ height: 'calc(100vh - 16rem)' }}>
      <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">Email Draft</h2>
      <div className="border rounded-lg p-4 flex-1 overflow-y-auto bg-gradient-to-br from-blue-50 to-indigo-50">
        <ReactMarkdown components={MARKDOWN_COMPONENTS}>
          {emailBody}
        </ReactMarkdown>
      </div>
    </div>
  );
}
