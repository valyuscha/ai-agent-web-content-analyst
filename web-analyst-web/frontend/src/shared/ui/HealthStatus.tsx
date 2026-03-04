/**
 * Health status banner component
 */
'use client';

interface HealthStatusProps {
  openaiConfigured: boolean | null;
  checkingHealth: boolean;
}

export default function HealthStatus({ openaiConfigured, checkingHealth }: HealthStatusProps) {
  if (checkingHealth) return null;

  if (openaiConfigured === false) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <p className="text-yellow-800 font-medium">⚠️ Backend Configuration Issue</p>
        <p className="text-yellow-700 text-sm mt-1">
          OpenAI API key not configured. Please set OPENAI_API_KEY in backend/.env
        </p>
      </div>
    );
  }

  return null;
}
