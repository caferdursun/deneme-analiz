import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyticsAPI } from '../api/client';
import type { SubjectAnalytics } from '../types';

export const LearningOutcomesPage: React.FC = () => {
  const [allOutcomes, setAllOutcomes] = useState<any[]>([]);
  const [filteredOutcomes, setFilteredOutcomes] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [availableSubjects, setAvailableSubjects] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadAllLearningOutcomes();
  }, []);

  useEffect(() => {
    if (selectedSubject === 'all') {
      setFilteredOutcomes(allOutcomes);
    } else {
      setFilteredOutcomes(allOutcomes.filter(o => o.subject_name === selectedSubject));
    }
  }, [selectedSubject, allOutcomes]);

  const loadAllLearningOutcomes = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get overview to get all subjects
      const overview = await analyticsAPI.getOverview();
      const subjects = [...new Set([...overview.top_subjects, ...overview.weak_subjects].map(s => s.subject_name))];
      setAvailableSubjects(subjects);

      // Load learning outcomes for all subjects
      const allOutcomesData: any[] = [];
      for (const subject of subjects) {
        try {
          const subjectData: SubjectAnalytics = await analyticsAPI.getSubjectAnalytics(subject);
          allOutcomesData.push(...subjectData.learning_outcomes.map(lo => ({
            ...lo,
            subject_name: subject
          })));
        } catch (err) {
          console.error(`Error loading outcomes for ${subject}:`, err);
        }
      }

      setAllOutcomes(allOutcomesData);
      setFilteredOutcomes(allOutcomesData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kazanımlar yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const getSuccessRateColor = (rate: number): string => {
    if (rate >= 80) return 'bg-green-100 text-green-700';
    if (rate >= 60) return 'bg-blue-100 text-blue-700';
    if (rate >= 40) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  const getSuccessRateLabel = (rate: number): string => {
    if (rate >= 80) return 'Çok İyi';
    if (rate >= 60) return 'İyi';
    if (rate >= 40) return 'Orta';
    return 'Zayıf';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Kazanımlar yükleniyor...</p>
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
            onClick={() => navigate('/dashboard')}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            ← Dashboard'a Dön
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
            <h1 className="text-3xl font-bold text-gray-900">Kazanımlar (Öğrenme Çıktıları)</h1>
          </div>

          {/* Subject Filter */}
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Ders:</label>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Tümü</option>
              {availableSubjects.map((subject) => (
                <option key={subject} value={subject}>
                  {subject}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Toplam Kazanım</p>
            <p className="text-3xl font-bold text-blue-600">{filteredOutcomes.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Çok İyi (&gt;80%)</p>
            <p className="text-3xl font-bold text-green-600">
              {filteredOutcomes.filter(o => o.average_success_rate >= 80).length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Orta (40-80%)</p>
            <p className="text-3xl font-bold text-yellow-600">
              {filteredOutcomes.filter(o => o.average_success_rate >= 40 && o.average_success_rate < 80).length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Zayıf (&lt;40%)</p>
            <p className="text-3xl font-bold text-red-600">
              {filteredOutcomes.filter(o => o.average_success_rate < 40).length}
            </p>
          </div>
        </div>

        {/* Learning Outcomes Table */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">
            Kazanım Listesi
            {selectedSubject !== 'all' && ` - ${selectedSubject}`}
          </h2>

          {filteredOutcomes.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Kazanım verisi bulunamadı.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Ders</th>
                    <th className="px-4 py-2 text-left">Kategori</th>
                    <th className="px-4 py-2 text-left">Alt Kategori</th>
                    <th className="px-4 py-2 text-left">Kazanım Açıklaması</th>
                    <th className="px-4 py-2 text-center">Görülme</th>
                    <th className="px-4 py-2 text-center">Soru</th>
                    <th className="px-4 py-2 text-center">Kazanılan</th>
                    <th className="px-4 py-2 text-center">Başarı Oranı</th>
                    <th className="px-4 py-2 text-center">Durum</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOutcomes
                    .sort((a, b) => a.average_success_rate - b.average_success_rate)
                    .map((outcome, index) => (
                      <tr key={index} className="border-t hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <button
                            onClick={() => navigate(`/subjects/${encodeURIComponent(outcome.subject_name)}`)}
                            className="text-blue-600 hover:text-blue-800 font-medium"
                          >
                            {outcome.subject_name}
                          </button>
                        </td>
                        <td className="px-4 py-3">{outcome.category || '-'}</td>
                        <td className="px-4 py-3">{outcome.subcategory || '-'}</td>
                        <td className="px-4 py-3 max-w-md">{outcome.outcome_description || '-'}</td>
                        <td className="px-4 py-3 text-center">{outcome.total_appearances}</td>
                        <td className="px-4 py-3 text-center">{outcome.total_questions}</td>
                        <td className="px-4 py-3 text-center">{outcome.total_acquired}</td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getSuccessRateColor(outcome.average_success_rate)}`}>
                            %{outcome.average_success_rate.toFixed(1)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-2 py-1 rounded text-xs ${getSuccessRateColor(outcome.average_success_rate)}`}>
                            {getSuccessRateLabel(outcome.average_success_rate)}
                          </span>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Help Text */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Not:</strong> Kazanımlar sınavlardaki soruların hangi konuları kapsadığını gösterir.
            Zayıf görünen kazanımlar üzerinde daha fazla çalışma yapılması önerilir.
          </p>
        </div>
      </div>
    </div>
  );
};
