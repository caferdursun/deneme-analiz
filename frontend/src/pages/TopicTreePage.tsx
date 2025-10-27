import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TreeNode, TreeNodeData } from '../components/TreeNode';
import { analyticsAPI } from '../api/client';

export const TopicTreePage: React.FC = () => {
  const [treeData, setTreeData] = useState<TreeNodeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRate, setFilterRate] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const navigate = useNavigate();

  useEffect(() => {
    loadTreeData();
  }, []);

  const loadTreeData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await analyticsAPI.getLearningOutcomesTree();
      setTreeData(response.tree || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ağaç verisi yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleOutcomeClick = (outcomeName: string) => {
    // Navigate to recommendations or learning outcomes page with filter
    // For now, just navigate to recommendations page
    navigate('/recommendations');
  };

  // Filter tree data based on search and filter rate
  const filterTree = (nodes: TreeNodeData[]): TreeNodeData[] => {
    return nodes
      .map(node => {
        // Apply success rate filter
        if (filterRate !== 'all') {
          const rate = node.stats.average_success_rate;
          if (
            (filterRate === 'high' && rate < 75) ||
            (filterRate === 'medium' && (rate < 50 || rate >= 75)) ||
            (filterRate === 'low' && rate >= 50)
          ) {
            return null;
          }
        }

        // Apply search query
        if (searchQuery && !node.name.toLowerCase().includes(searchQuery.toLowerCase())) {
          // If node doesn't match, check children
          if (node.children) {
            const filteredChildren = filterTree(node.children);
            if (filteredChildren.length === 0) {
              return null;
            }
            return { ...node, children: filteredChildren };
          }
          return null;
        }

        // Recursively filter children
        if (node.children) {
          const filteredChildren = filterTree(node.children);
          return { ...node, children: filteredChildren };
        }

        return node;
      })
      .filter(Boolean) as TreeNodeData[];
  };

  const filteredData = filterTree(treeData);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Konu ağacı yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-red-50 p-6 rounded-lg max-w-md">
          <p className="text-red-700 font-medium">Hata</p>
          <p className="text-red-600 text-sm mt-2">{error}</p>
          <button
            onClick={loadTreeData}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Tekrar dene
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 sm:py-8 px-3 sm:px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2 text-sm sm:text-base"
          >
            ← Geri
          </button>

          <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
              Konu Ağacı 🌳
            </h1>
            <p className="text-sm sm:text-base text-gray-600 mb-6">
              Tüm kazanımlar hiyerarşik yapıda gösteriliyor. Başarı oranına göre renk kodlu.
            </p>

            {/* Search and Filter */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ara
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Konu veya kazanım ara..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Filter by success rate */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Başarı Oranı Filtresi
                </label>
                <select
                  value={filterRate}
                  onChange={(e) => setFilterRate(e.target.value as any)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">Tümü</option>
                  <option value="high">Yüksek (≥75%)</option>
                  <option value="medium">Orta (50-74%)</option>
                  <option value="low">Düşük (&lt;50%)</option>
                </select>
              </div>
            </div>

            {/* Legend */}
            <div className="mt-6 flex flex-wrap gap-4 text-xs sm:text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-200 border-2 border-green-400 rounded"></div>
                <span>Yüksek (≥75%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-200 border-2 border-yellow-400 rounded"></div>
                <span>Orta (50-74%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-200 border-2 border-red-400 rounded"></div>
                <span>Düşük (&lt;50%)</span>
              </div>
              <div className="flex items-center gap-2">
                <span>💡</span>
                <span>Öneriler var</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tree */}
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
          {filteredData.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              {searchQuery || filterRate !== 'all'
                ? 'Filtre kriterlerine uygun sonuç bulunamadı.'
                : 'Henüz kazanım verisi yok.'}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredData.map((node, index) => (
                <TreeNode
                  key={`${node.name}-${index}`}
                  node={node}
                  level={0}
                  onOutcomeClick={handleOutcomeClick}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopicTreePage;
