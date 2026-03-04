'use client';

interface DownloadButtonsProps {
  sessionId: string | null;
  getExportUrl: (sessionId: string, format: 'md' | 'json') => string;
}

export default function DownloadButtons({ sessionId, getExportUrl }: DownloadButtonsProps) {
  if (!sessionId) return null;

  return (
    <div className="flex gap-3">
      <a
        href={getExportUrl(sessionId, 'md')}
        download
        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
      >
        📥 Download Markdown
      </a>
      <a
        href={getExportUrl(sessionId, 'json')}
        download
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        📥 Download JSON
      </a>
    </div>
  );
}
