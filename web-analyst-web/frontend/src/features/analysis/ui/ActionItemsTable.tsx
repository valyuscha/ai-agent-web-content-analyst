'use client';

interface ActionItem {
  task: string;
  owner: string;
  due_date: string;
  priority: string;
  confidence: number;
  source_quote: string;
}

interface ActionItemsTableProps {
  resultJson: any;
  onRecheck: () => void;
  loading: boolean;
}

export default function ActionItemsTable({ resultJson, onRecheck, loading }: ActionItemsTableProps) {
  const allItems: (ActionItem & { source: string })[] = [];
  
  resultJson?.sources?.forEach((source: any) => {
    source.action_items?.forEach((item: ActionItem) => {
      allItems.push({ ...item, source: source.title });
    });
  });

  const lowConfCount = allItems.filter(item => item.confidence < 0.55).length;
  const avgConf = allItems.length > 0 
    ? allItems.reduce((sum, item) => sum + item.confidence, 0) / allItems.length 
    : 0;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Action Items</h2>
        <button
          onClick={onRecheck}
          disabled={loading || lowConfCount === 0}
          className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Re-checking...' : '🔄 Re-check Low Confidence'}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Total Items</p>
          <p className="text-2xl font-bold">{allItems.length}</p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Low Confidence</p>
          <p className="text-2xl font-bold">{lowConfCount}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Avg Confidence</p>
          <p className="text-2xl font-bold">{avgConf.toFixed(2)}</p>
        </div>
      </div>

      {allItems.length === 0 ? (
        <p className="text-gray-500">No action items extracted yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 text-left">Source</th>
                <th className="p-2 text-left">Task</th>
                <th className="p-2 text-left">Owner</th>
                <th className="p-2 text-left">Due Date</th>
                <th className="p-2 text-left">Priority</th>
                <th className="p-2 text-left">Confidence</th>
                <th className="p-2 text-left">Quote</th>
              </tr>
            </thead>
            <tbody>
              {allItems.map((item, index) => (
                <tr 
                  key={index} 
                  className={`border-b ${item.confidence < 0.55 ? 'bg-red-50' : ''}`}
                >
                  <td className="p-2 text-xs text-gray-600">{item.source}</td>
                  <td className="p-2 font-medium">{item.task}</td>
                  <td className="p-2">{item.owner}</td>
                  <td className="p-2">{item.due_date}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      item.priority === 'high' ? 'bg-red-100 text-red-800' :
                      item.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="p-2">
                    <span className={`font-semibold ${
                      item.confidence < 0.55 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {item.confidence.toFixed(2)}
                    </span>
                  </td>
                  <td className="p-2 text-xs text-gray-600 italic max-w-xs truncate">
                    {item.source_quote || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
