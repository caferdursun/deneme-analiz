import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recommendationsAPI } from '../api/client';
import type { Recommendation } from '../types';

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await recommendationsAPI.getRecommendations();
      setRecommendations(data.recommendations);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Öneriler yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      setError(null);
      const data = await recommendationsAPI.refreshRecommendations();
      setRecommendations(data.recommendations);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Öneriler yenilenirken hata oluştu');
    } finally {
      setRefreshing(false);
    }
  };

  const handleMarkComplete = async (id: string) => {
    try {
      await recommendationsAPI.markAsComplete(id);
      // Remove from list
      setRecommendations(prev => prev.filter(r => r.id !== id));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Öneri tamamlanırken hata oluştu');
    }
  };

  const getPriorityColor = (priority: number): string => {
    if (priority === 1) return 'bg-red-100 text-red-700 border-red-300';
    if (priority === 2) return 'bg-orange-100 text-orange-700 border-orange-300';
    if (priority === 3) return 'bg-yellow-100 text-yellow-700 border-yellow-300';
    return 'bg-gray-100 text-gray-700 border-gray-300';
  };

  const getPriorityLabel = (priority: number): string => {
    if (priority === 1) return 'Çok Önemli';
    if (priority === 2) return 'Önemli';
    if (priority === 3) return 'Orta';
    return 'Düşük';
  };

  const getIssueTypeLabel = (issueType: string): string => {
    const labels: Record<string, string> = {
      'weak_subject': 'Zayıf Ders',
      'declining_trend': 'Düşüş Trendi',
      'high_blank_rate': 'Boş Bırakma',
      'weak_outcomes': 'Zayıf Kazanımlar',
    };
    return labels[issueType] || issueType;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Öneriler yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 p-6 rounded-lg max-w-md">
          <p className="text-red-700 font-medium">Hata</p>
          <p className="text-red-600 text-sm mt-2">{error}</p>
          <button
            onClick={loadRecommendations}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Tekrar dene
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Geri
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Çalışma Önerileri</h1>
          </div>

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-400 text-sm font-medium flex items-center gap-2"
          >
            {refreshing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Yenileniyor...
              </>
            ) : (
              '🔄 Yenile'
            )}
          </button>
        </div>

        {recommendations.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 text-lg mb-4">Henüz öneri bulunamadı</p>
            <p className="text-gray-400 text-sm mb-6">
              Öneriler oluşturmak için "Yenile" butonuna tıklayın
            </p>
            <button
              onClick={handleRefresh}
              className="bg-blue-600 text-white py-2 px-6 rounded-md hover:bg-blue-700 text-sm font-medium"
            >
              Öneriler Oluştur
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className={`bg-white rounded-lg shadow-md border-l-4 overflow-hidden ${
                  rec.priority === 1 ? 'border-red-500' :
                  rec.priority === 2 ? 'border-orange-500' :
                  rec.priority === 3 ? 'border-yellow-500' :
                  'border-gray-300'
                }`}
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(rec.priority)}`}>
                          {getPriorityLabel(rec.priority)}
                        </span>
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                          {getIssueTypeLabel(rec.issue_type)}
                        </span>
                        {rec.subject_name && (
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                            {rec.subject_name}
                          </span>
                        )}
                      </div>
                      {rec.topic && (
                        <p className="text-sm text-gray-600 mb-1">{rec.topic}</p>
                      )}
                      <h3 className="text-lg font-bold text-gray-900">{rec.description}</h3>
                    </div>
                    {rec.impact_score && (
                      <div className="ml-4 text-center">
                        <div className="text-2xl font-bold text-blue-600">{rec.impact_score.toFixed(1)}</div>
                        <div className="text-xs text-gray-500">Etki Skoru</div>
                      </div>
                    )}
                  </div>

                  {/* Rationale */}
                  {rec.rationale && (
                    <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700"><strong>Neden:</strong> {rec.rationale}</p>
                    </div>
                  )}

                  {/* Action Items */}
                  {rec.action_items && rec.action_items.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-gray-900 mb-2">Yapılacaklar:</h4>
                      <ul className="space-y-2">
                        {rec.action_items.map((item, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="text-green-600 mt-0.5">✓</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t">
                    <span className="text-xs text-gray-500">
                      Oluşturulma: {new Date(rec.generated_at).toLocaleDateString('tr-TR')}
                    </span>
                    <button
                      onClick={() => handleMarkComplete(rec.id)}
                      className="bg-green-600 text-white py-1 px-4 rounded-md hover:bg-green-700 text-sm font-medium"
                    >
                      Tamamlandı İşaretle
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Help Text */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>İpucu:</strong> Öneriler, sınav performansınız analiz edilerek otomatik oluşturulur.
            Yeni sınav ekledikten sonra "Yenile" butonuna tıklayarak güncel öneriler alabilirsiniz.
          </p>
        </div>
      </div>
    </div>
  );
};
