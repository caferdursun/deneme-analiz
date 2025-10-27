import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { learningOutcomesAPI } from '../api/client';

type CleanupStep = 'initial' | 'analyzing' | 'review' | 'confirming' | 'results';

interface SimilarityGroup {
  group_id: string;
  confidence_score: number;
  suggested_name: string;
  reason: string;
  outcome_ids: string[];
  total_questions: number;
  outcomes: any[];
}

export const CleanupWizardPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<CleanupStep>('initial');
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [selectedGroups, setSelectedGroups] = useState<Set<string>>(new Set());
  const [cleanupResults, setCleanupResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const startAnalysis = async () => {
    setStep('analyzing');
    setError(null);

    try {
      const data = await learningOutcomesAPI.analyzeOutcomes();
      setAnalysisData(data);

      // Auto-select high confidence groups (>=90%)
      const autoSelect = new Set<string>();
      data.similarity_groups?.forEach((group: SimilarityGroup) => {
        if (group.confidence_score >= 90) {
          autoSelect.add(group.group_id);
        }
      });
      setSelectedGroups(autoSelect);

      setStep('review');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analiz sırasında bir hata oluştu');
      setStep('initial');
    }
  };

  const toggleGroupSelection = (groupId: string) => {
    const newSelected = new Set(selectedGroups);
    if (newSelected.has(groupId)) {
      newSelected.delete(groupId);
    } else {
      newSelected.add(groupId);
    }
    setSelectedGroups(newSelected);
  };

  const selectAllHighConfidence = () => {
    const highConfGroups = new Set<string>();
    analysisData.similarity_groups?.forEach((group: SimilarityGroup) => {
      if (group.confidence_score >= 90) {
        highConfGroups.add(group.group_id);
      }
    });
    setSelectedGroups(highConfGroups);
  };

  const performCleanup = async () => {
    setStep('confirming');
    setError(null);

    try {
      const groupsToMerge = analysisData.similarity_groups.filter((group: SimilarityGroup) =>
        selectedGroups.has(group.group_id)
      );

      const results = await learningOutcomesAPI.cleanupOutcomes(groupsToMerge);
      setCleanupResults(results);
      setStep('results');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Temizleme sırasında bir hata oluştu');
      setStep('review');
    }
  };

  const getConfidenceColor = (score: number): string => {
    if (score >= 90) return 'border-green-500 bg-green-50';
    if (score >= 80) return 'border-yellow-500 bg-yellow-50';
    return 'border-orange-500 bg-orange-50';
  };

  const getConfidenceBadge = (score: number): string => {
    if (score >= 90) return 'bg-green-100 text-green-800';
    if (score >= 80) return 'bg-yellow-100 text-yellow-800';
    return 'bg-orange-100 text-orange-800';
  };

  const getConfidenceLabel = (score: number): string => {
    if (score >= 90) return 'Yüksek Güven';
    if (score >= 80) return 'Orta Güven';
    return 'Düşük Güven';
  };

  // Initial Step
  if (step === 'initial') {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <button
              onClick={() => navigate('/learning-outcomes/tree')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Geri
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Kazanımları Temizle</h1>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800 font-medium">Hata</p>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          )}

          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">🧹</div>
              <h2 className="text-2xl font-bold mb-2">Kazanım Temizleme Aracı</h2>
              <p className="text-gray-600">
                Claude AI kullanarak benzer kazanımları tespit edin ve birleştirin
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800 font-medium mb-2">Bu araç ne yapar?</p>
              <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
                <li>Farklı sınavlardan gelen benzer kazanımları bulur</li>
                <li>Aynı anlama gelen ama farklı yazılan kazanımları birleştirir</li>
                <li>Türkçe dil varyasyonlarını akıllıca tanır</li>
                <li>Her birleştirme işlemi geri alınabilir</li>
              </ul>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-yellow-800 font-medium mb-2">⚠️ Dikkat</p>
              <ul className="text-sm text-yellow-700 space-y-1 list-disc list-inside">
                <li>Analiz işlemi 30-60 saniye sürebilir</li>
                <li>Yüksek güvenilirlik skorlu (&gt;90%) birleştirmeler otomatik seçilir</li>
                <li>Her birleştirme işleminden önce onayınız alınacak</li>
              </ul>
            </div>

            <button
              onClick={startAnalysis}
              className="w-full bg-purple-600 text-white py-4 rounded-lg hover:bg-purple-700 transition-colors text-lg font-medium"
            >
              ✨ Claude AI ile Analiz Başlat
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Analyzing Step
  if (step === 'analyzing') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold mb-2">Kazanımlar Analiz Ediliyor...</h2>
          <p className="text-gray-600 mb-4">
            Claude AI benzer kazanımları tespit ediyor. Bu işlem 30-60 saniye sürebilir.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              ☕ Lütfen bekleyin, sayfayı kapatmayın...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Review Step
  if (step === 'review' && analysisData) {
    const similarityGroups: SimilarityGroup[] = analysisData.similarity_groups || [];
    const selectedCount = selectedGroups.size;
    const totalOutcomesToMerge = similarityGroups
      .filter(g => selectedGroups.has(g.group_id))
      .reduce((acc, g) => acc + g.outcome_ids.length, 0);

    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <button
              onClick={() => navigate('/learning-outcomes/tree')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← İptal
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Analiz Sonuçları</h1>
          </div>

          {/* Summary */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow-lg p-6 mb-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold">✅ Analiz Tamamlandı!</h2>
                <p className="text-sm text-gray-700 mt-1">
                  {analysisData.total_outcomes} kazanım analiz edildi, {similarityGroups.length} benzerlik grubu bulundu
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600">Yüksek Güven (&gt;90%)</p>
                <p className="text-2xl font-bold text-green-600">{analysisData.high_confidence_count || 0}</p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600">Orta Güven (80-90%)</p>
                <p className="text-2xl font-bold text-yellow-600">{analysisData.medium_confidence_count || 0}</p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600">Düşük Güven (&lt;80%)</p>
                <p className="text-2xl font-bold text-orange-600">{analysisData.low_confidence_count || 0}</p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-4 mb-6 flex items-center justify-between">
            <div>
              <p className="font-medium">
                {selectedCount} grup seçildi ({totalOutcomesToMerge} kazanım birleştirilecek)
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={selectAllHighConfidence}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm font-medium"
              >
                Yüksek Güvenlileri Seç
              </button>
              <button
                onClick={() => setSelectedGroups(new Set())}
                className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 text-sm font-medium"
              >
                Tümünü Kaldır
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800 font-medium">Hata</p>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          )}

          {/* Similarity Groups */}
          {similarityGroups.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <p className="text-gray-500">Benzer kazanım bulunamadı. Tüm kazanımlar zaten temiz!</p>
            </div>
          ) : (
            <div className="space-y-4 mb-6">
              {similarityGroups.map((group) => {
                const isSelected = selectedGroups.has(group.group_id);

                return (
                  <div
                    key={group.group_id}
                    className={`bg-white rounded-lg shadow-md p-6 border-2 transition-all cursor-pointer ${
                      isSelected ? getConfidenceColor(group.confidence_score) + ' border-opacity-100' : 'border-gray-200'
                    }`}
                    onClick={() => toggleGroupSelection(group.group_id)}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleGroupSelection(group.group_id)}
                          className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500"
                          onClick={(e) => e.stopPropagation()}
                        />
                        <div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getConfidenceBadge(group.confidence_score)}`}>
                            {getConfidenceLabel(group.confidence_score)} - %{group.confidence_score.toFixed(0)}
                          </span>
                        </div>
                      </div>
                      <div className="text-right text-sm text-gray-600">
                        {group.outcome_ids.length} kazanım • {group.total_questions} soru
                      </div>
                    </div>

                    <div className="mb-3">
                      <p className="font-semibold text-lg text-gray-900 mb-1">
                        📝 Önerilen İsim: "{group.suggested_name}"
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Neden benzer:</strong> {group.reason}
                      </p>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Birleştirilecek kazanımlar:</p>
                      <ul className="space-y-1">
                        {group.outcomes.map((outcome: any, idx: number) => (
                          <li key={idx} className="text-sm text-gray-600">
                            • {outcome.description || outcome.category || 'İsimsiz kazanım'} ({outcome.subject})
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-4 sticky bottom-4">
            <button
              onClick={() => navigate('/learning-outcomes/tree')}
              className="bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 font-medium"
            >
              İptal
            </button>
            <button
              onClick={performCleanup}
              disabled={selectedCount === 0}
              className="bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {selectedCount > 0
                ? `${selectedCount} Grubu Birleştir (${totalOutcomesToMerge} kazanım)`
                : 'Hiçbir grup seçilmedi'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Confirming Step
  if (step === 'confirming') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold mb-2">Birleştirme İşlemi Yapılıyor...</h2>
          <p className="text-gray-600 mb-4">Kazanımlar birleştiriliyor, lütfen bekleyin.</p>
        </div>
      </div>
    );
  }

  // Results Step
  if (step === 'results' && cleanupResults) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">✅</div>
              <h2 className="text-2xl font-bold mb-2">Temizleme Tamamlandı!</h2>
              <p className="text-gray-600">
                Kazanım birleştirme işlemi başarıyla tamamlandı
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 mb-1">Toplam Grup</p>
                <p className="text-3xl font-bold text-blue-600">{cleanupResults.total_groups}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 mb-1">Başarılı</p>
                <p className="text-3xl font-bold text-green-600">{cleanupResults.merged_count}</p>
              </div>
              <div className="bg-red-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 mb-1">Başarısız</p>
                <p className="text-3xl font-bold text-red-600">{cleanupResults.failed_count}</p>
              </div>
            </div>

            {cleanupResults.failed_count > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-yellow-800">
                  ⚠️ Bazı birleştirmeler başarısız oldu. Detaylar için geçmişi kontrol edin.
                </p>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800">
                💡 Tüm birleştirme işlemleri geri alınabilir. Merge History sayfasından
                istediğiniz zaman eski haline döndürebilirsiniz.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => navigate('/learning-outcomes/tree')}
                className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 font-medium"
              >
                Kazanımlara Dön
              </button>
              <button
                onClick={() => window.location.reload()}
                className="flex-1 bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 font-medium"
              >
                Yeni Temizleme
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};
