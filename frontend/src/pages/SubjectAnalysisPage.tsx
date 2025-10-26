import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsAPI } from '../api/client';
import type { SubjectAnalytics } from '../types';

export const SubjectAnalysisPage: React.FC = () => {
  const { subjectName } = useParams<{ subjectName: string }>();
  const [analytics, setAnalytics] = useState<SubjectAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (subjectName) {
      loadAnalytics();
    }
  }, [subjectName]);

  const loadAnalytics = async () => {
    if (!subjectName) return;

    try {
      setLoading(true);
      setError(null);
      const data = await analyticsAPI.getSubjectAnalytics(subjectName);
      setAnalytics(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ders analizi yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Ders analizi yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 p-6 rounded-lg max-w-md">
          <p className="text-red-700 font-medium">Hata</p>
          <p className="text-red-600 text-sm mt-2">{error || 'Veri bulunamadı'}</p>
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

  const { performance, trends, learning_outcomes } = analytics;

  // Shorten exam names for better display
  const formatExamName = (name: string, index: number) => {
    const dateMatch = name.match(/(\d{1,2})\s*(HAZİRAN|TEMMUZ|AĞUSTOS|EYLÜL|EKİM|KASIM|ARALIK|OCAK|ŞUBAT|MART|NİSAN|MAYIS)/i);
    if (dateMatch) {
      return `${dateMatch[1]} ${dateMatch[2]}`;
    }
    return `Sınav ${index + 1}`;
  };

  const formattedTrends = trends.map((trend, index) => ({
    ...trend,
    short_name: formatExamName(trend.exam_name, index),
  }));

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Geri
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{subjectName} - Ders Analizi</h1>
        </div>

        {/* Performance Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Sınav Sayısı</p>
            <p className="text-3xl font-bold text-blue-600">{performance.total_exams}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Ortalama Net</p>
            <p className="text-3xl font-bold text-green-600">{performance.average_net.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">En İyi Net</p>
            <p className="text-3xl font-bold text-purple-600">{performance.best_net.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Başarı Oranı</p>
            <p className="text-3xl font-bold text-yellow-600">%{performance.average_percentage.toFixed(1)}</p>
          </div>
        </div>

        {/* Trend Indicator */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Gelişim Durumu</h2>
          <div className="flex items-center gap-4">
            <span className={`px-4 py-2 rounded-lg text-lg font-medium ${
              performance.improvement_trend === 'improving' ? 'bg-green-100 text-green-700' :
              performance.improvement_trend === 'declining' ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {performance.improvement_trend === 'improving' ? '↑ Gelişiyor' :
               performance.improvement_trend === 'declining' ? '↓ Düşüyor' :
               '→ Stabil'}
            </span>
            <div className="text-sm text-gray-600">
              <p>Toplam Soru: {performance.total_questions}</p>
              <p>Doğru: {performance.total_correct} | Yanlış: {performance.total_wrong} | Boş: {performance.total_blank}</p>
            </div>
          </div>
        </div>

        {/* Net Score Trend Chart */}
        {formattedTrends.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">Net Skor Gelişimi</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formattedTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="short_name" height={60} tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
                          <p className="text-sm font-medium mb-1">{data.exam_name}</p>
                          <p className="text-sm text-blue-600">Net Skor: {data.net_score}</p>
                          <p className="text-sm text-gray-600">Net %: {data.net_percentage.toFixed(1)}%</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="net_score" stroke="#3b82f6" name="Net Skor" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Question Distribution */}
        {formattedTrends.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">Soru Dağılımı (Sınavlara Göre)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={formattedTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="short_name" height={60} tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
                          <p className="text-sm font-medium mb-1">{data.exam_name}</p>
                          <p className="text-sm text-green-600">Doğru: {data.correct}</p>
                          <p className="text-sm text-red-600">Yanlış: {data.wrong}</p>
                          <p className="text-sm text-gray-600">Boş: {data.blank}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend />
                <Bar dataKey="correct" fill="#10b981" name="Doğru" />
                <Bar dataKey="wrong" fill="#ef4444" name="Yanlış" />
                <Bar dataKey="blank" fill="#9ca3af" name="Boş" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Learning Outcomes */}
        {learning_outcomes.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Kazanımlar (Öğrenme Çıktıları)</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Kategori</th>
                    <th className="px-4 py-2 text-left">Alt Kategori</th>
                    <th className="px-4 py-2 text-left">Kazanım</th>
                    <th className="px-4 py-2 text-center">Soru Sayısı</th>
                    <th className="px-4 py-2 text-center">Kazanılan</th>
                    <th className="px-4 py-2 text-center">Başarı Oranı</th>
                  </tr>
                </thead>
                <tbody>
                  {learning_outcomes.map((outcome, index) => (
                    <tr key={index} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3">{outcome.category || '-'}</td>
                      <td className="px-4 py-3">{outcome.subcategory || '-'}</td>
                      <td className="px-4 py-3">{outcome.outcome_description || '-'}</td>
                      <td className="px-4 py-3 text-center">{outcome.total_questions}</td>
                      <td className="px-4 py-3 text-center">{outcome.total_acquired}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`px-2 py-1 rounded text-xs ${
                          outcome.average_success_rate >= 70 ? 'bg-green-100 text-green-700' :
                          outcome.average_success_rate >= 50 ? 'bg-yellow-100 text-yellow-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          %{outcome.average_success_rate.toFixed(1)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {learning_outcomes.length === 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-500 text-center">Bu ders için kazanım verisi bulunamadı.</p>
          </div>
        )}
      </div>
    </div>
  );
};
