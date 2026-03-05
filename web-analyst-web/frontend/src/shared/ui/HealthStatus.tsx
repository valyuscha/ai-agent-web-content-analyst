import { HealthStatusProps } from './HealthStatus.types';

export default function HealthStatus({ checking, configured }: HealthStatusProps) {
  if (checking) {
    return (
      <div className="px-4 py-2 rounded-lg bg-blue-100 text-blue-800">
        <span className="animate-pulse">⏳ Checking Server...</span>
      </div>
    );
  }

  if (configured === null) return null;

  return (
    <div className={`px-4 py-2 rounded-lg ${
      configured ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    }`}>
      {configured ? '✓ OpenAI Configured' : '✗ OpenAI Not Configured'}
    </div>
  );
}
