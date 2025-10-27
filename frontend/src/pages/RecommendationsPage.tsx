import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { recommendationsAPI } from '../api/client';
import type { Recommendation, RefreshSummary } from '../types';
import { RecommendationsSkeleton } from '../components/Skeleton';

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshSummary, setRefreshSummary] = useState<RefreshSummary | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
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
    const toastId = toast.loading('Öneriler AI ile yenileniyor...');

    try {
      setRefreshing(true);
      setError(null);
      const data = await recommendationsAPI.refreshRecommendations();
      setRecommendations(data.recommendations);
      setRefreshSummary(data.summary);

      // Show success toast
      const summary = data.summary;
      const message = `✓ ${summary.new_count} yeni, ${summary.updated_count} güncellendi, ${summary.confirmed_count} onaylandı`;
      toast.success(message, { id: toastId, duration: 4000 });

      // Auto-hide summary after 5 seconds
      setTimeout(() => setRefreshSummary(null), 5000);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Öneriler yenilenirken hata oluştu';
      toast.error(errorMsg, { id: toastId });
      setError(errorMsg);
    } finally {
      setRefreshing(false);
    }
  };

  const handleMarkComplete = async (id: string) => {
    try {
      await recommendationsAPI.markAsComplete(id);
      // Remove from list
      setRecommendations(prev => prev.filter(r => r.id !== id));
      toast.success('✓ Öneri tamamlandı olarak işaretlendi', { duration: 2000 });
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Öneri tamamlanırken hata oluştu';
      toast.error(errorMsg);
      setError(errorMsg);
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
      'top_3_weakest_outcomes': 'En Zayıf Konular',
      'outcomes_below_80': '%80 Altı Kazanımlar',
    };
    return labels[issueType] || issueType;
  };

  const getStatusBadge = (status: string): { color: string; label: string } => {
    switch (status) {
      case 'new':
        return { color: 'bg-green-100 text-green-700 border-green-300', label: 'YENİ' };
      case 'updated':
        return { color: 'bg-blue-100 text-blue-700 border-blue-300', label: 'GÜNCELLENDİ' };
      case 'active':
        return { color: 'bg-gray-100 text-gray-700 border-gray-300', label: 'AKTİF' };
      default:
        return { color: 'bg-gray-100 text-gray-700 border-gray-300', label: status.toUpperCase() };
    }
  };

  const filteredRecommendations = recommendations.filter(rec => {
    if (statusFilter === 'all') return true;
    return rec.status === statusFilter;
  });

  if (loading) {
    return <RecommendationsSkeleton />;
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

        {/* Summary Message after Refresh */}
        {refreshSummary && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
            <span className="text-green-600 text-xl">✅</span>
            <div className="flex-1">
              <p className="text-sm font-medium text-green-800">
                Öneriler güncellendi
              </p>
              <p className="text-sm text-green-700 mt-1">
                {refreshSummary.new_count} yeni, {refreshSummary.updated_count} güncellendi,
                {' '}{refreshSummary.confirmed_count} onaylandı, {refreshSummary.resolved_count} çözüldü
              </p>
              <p className="text-xs text-green-600 mt-1">
                Toplam {refreshSummary.total_active} aktif öneri
              </p>
            </div>
            <button
              onClick={() => setRefreshSummary(null)}
              className="text-green-600 hover:text-green-800"
            >
              ✕
            </button>
          </div>
        )}

        {/* Status Filter Tabs */}
        {recommendations.length > 0 && (
          <div className="mb-6 flex gap-2 border-b border-gray-200">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                statusFilter === 'all'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Tümü ({recommendations.length})
            </button>
            <button
              onClick={() => setStatusFilter('new')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                statusFilter === 'new'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Yeni ({recommendations.filter(r => r.status === 'new').length})
            </button>
            <button
              onClick={() => setStatusFilter('updated')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                statusFilter === 'updated'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Güncellendi ({recommendations.filter(r => r.status === 'updated').length})
            </button>
            <button
              onClick={() => setStatusFilter('active')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                statusFilter === 'active'
                  ? 'border-gray-600 text-gray-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Aktif ({recommendations.filter(r => r.status === 'active').length})
            </button>
          </div>
        )}

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
            {filteredRecommendations.map((rec) => (
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
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        {/* Status Badge */}
                        <span className={`px-2 py-1 rounded text-xs font-bold border ${getStatusBadge(rec.status).color}`}>
                          {getStatusBadge(rec.status).label}
                        </span>
                        {/* Priority Badge */}
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(rec.priority)}`}>
                          {getPriorityLabel(rec.priority)}
                        </span>
                        {/* Issue Type Badge */}
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                          {getIssueTypeLabel(rec.issue_type)}
                        </span>
                        {/* Subject Badge */}
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

                  {/* Learning Outcome Details */}
                  {rec.learning_outcome_description && (
                    <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <p className="text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">
                            Kazanım Detayı
                          </p>
                          <p className="text-sm text-gray-700 mb-2 font-medium">
                            {rec.learning_outcome_description}
                          </p>
                          {/* Category Hierarchy */}
                          {(rec.learning_outcome_category || rec.learning_outcome_subcategory) && (
                            <div className="flex items-center gap-2 text-xs text-gray-600">
                              {rec.learning_outcome_category && (
                                <span className="px-2 py-0.5 bg-gray-200 rounded">
                                  {rec.learning_outcome_category}
                                </span>
                              )}
                              {rec.learning_outcome_category && rec.learning_outcome_subcategory && (
                                <span>→</span>
                              )}
                              {rec.learning_outcome_subcategory && (
                                <span className="px-2 py-0.5 bg-gray-200 rounded">
                                  {rec.learning_outcome_subcategory}
                                </span>
                              )}
                            </div>
                          )}
                        </div>

                        <div className="flex items-center gap-3">
                          {/* Success Rate Badge */}
                          {rec.learning_outcome_success_rate !== null && rec.learning_outcome_success_rate !== undefined && (
                            <div className="text-center">
                              <div
                                className={`text-lg font-bold px-3 py-1 rounded-lg ${
                                  rec.learning_outcome_success_rate >= 75
                                    ? 'bg-green-100 text-green-700'
                                    : rec.learning_outcome_success_rate >= 50
                                    ? 'bg-yellow-100 text-yellow-700'
                                    : 'bg-red-100 text-red-700'
                                }`}
                                title={`Başarı oranı: %${rec.learning_outcome_success_rate.toFixed(1)}`}
                              >
                                %{rec.learning_outcome_success_rate.toFixed(0)}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">Başarı</div>
                            </div>
                          )}

                          {/* Trend Indicator */}
                          {rec.learning_outcome_trend && (
                            <div className="text-center" title={
                              rec.learning_outcome_trend === 'improving' ? 'Yükseliyor' :
                              rec.learning_outcome_trend === 'declining' ? 'Düşüyor' : 'Sabit'
                            }>
                              <div className={`text-2xl ${
                                rec.learning_outcome_trend === 'improving' ? 'text-green-600' :
                                rec.learning_outcome_trend === 'declining' ? 'text-red-600' : 'text-gray-500'
                              }`}>
                                {rec.learning_outcome_trend === 'improving' ? '📈' :
                                 rec.learning_outcome_trend === 'declining' ? '📉' : '➡️'}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                {rec.learning_outcome_trend === 'improving' ? 'İlerliyor' :
                                 rec.learning_outcome_trend === 'declining' ? 'Geriliyor' : 'Sabit'}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
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
