/**
 * Tab navigation component
 */
'use client';

import { useSpaces } from '../../features/spaces/application/SpaceContext';

const tabs = [
  { id: 'input' as const, label: 'Input' },
  { id: 'sources' as const, label: 'Sources' },
  { id: 'results' as const, label: 'Results' },
  { id: 'email' as const, label: 'Email' },
  { id: 'log' as const, label: 'Log' },
];

export default function TabNavigation() {
  const { activeSpace, updateActiveSpace } = useSpaces();

  if (!activeSpace) return null;

  return (
    <div className="flex space-x-1 border-b border-gray-300 mb-6">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => updateActiveSpace({ ui: { ...activeSpace.ui, activeTab: tab.id } })}
          className={`px-4 py-2 font-medium transition-colors ${
            activeSpace.ui.activeTab === tab.id
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
