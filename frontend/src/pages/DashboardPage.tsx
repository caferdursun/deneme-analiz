import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsAPI } from '../api/client';
import type { AnalyticsOverview } from '../types';

export const DashboardPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsAPI.getOverview();
      setAnalytics(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analytics yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Analytics yükleniyor...</p>
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
            onClick={loadAnalytics}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Tekrar dene
          </button>
        </div>
      </div>
    );
  }

  const { stats, score_trends, top_subjects, weak_subjects } = analytics;

  // Shorten exam names for better display
  const formatExamName = (name: string, index: number) => {
    // Extract date if exists
    const dateMatch = name.match(/(\d{1,2})\s*(HAZİRAN|TEMMUZ|AĞUSTOS|EYLÜL|EKİM|KASIM|ARALIK|OCAK|ŞUBAT|MART|NİSAN|MAYIS)/i);
    if (dateMatch) {
      return `${dateMatch[1]} ${dateMatch[2]}`;
    }
    // Otherwise use "Sınav X"
    return `Sınav ${index + 1}`;
  };

  const formattedScoreTrends = score_trends.map((trend, index) => ({
    ...trend,
    short_name: formatExamName(trend.exam_name, index),
  }));

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/upload')}
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 text-sm font-medium"
            >
              + Yeni Sınav
            </button>
            <button
              onClick={() => navigate('/exams')}
              className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 text-sm font-medium"
            >
              Sınavlar
            </button>
            <button
              onClick={() => navigate('/learning-outcomes')}
              className="bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 text-sm font-medium"
            >
              Kazanımlar
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Toplam Sınav</p>
            <p className="text-3xl font-bold text-blue-600">{stats.total_exams}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Son Net</p>
            <p className="text-3xl font-bold text-green-600">
              {stats.latest_net_score?.toFixed(2) || '-'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Ortalama Net</p>
            <p className="text-3xl font-bold text-purple-600">
              {stats.average_net_score?.toFixed(2) || '-'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Doğruluk Oranı</p>
            <p className="text-3xl font-bold text-yellow-600">
              {stats.overall_accuracy ? `%${stats.overall_accuracy.toFixed(1)}` : '-'}
            </p>
          </div>
        </div>

        {/* Score Trend Chart */}
        {formattedScoreTrends.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">Net Skor Gelişimi</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formattedScoreTrends}>
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

        {/* Subject Performance */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Top Subjects */}
          {top_subjects.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4 text-green-600">En İyi Dersler</h2>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={top_subjects}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="subject_name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="average_percentage" fill="#10b981" name="Ortalama %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Weak Subjects */}
          {weak_subjects.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4 text-red-600">Gelişmesi Gereken Dersler</h2>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={weak_subjects}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="subject_name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="average_percentage" fill="#ef4444" name="Ortalama %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Subject Details Table */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Ders Detayları</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">Ders</th>
                  <th className="px-4 py-2 text-center">Sınav Sayısı</th>
                  <th className="px-4 py-2 text-center">Ort. Net</th>
                  <th className="px-4 py-2 text-center">En İyi</th>
                  <th className="px-4 py-2 text-center">Trend</th>
                </tr>
              </thead>
              <tbody>
                {[...top_subjects, ...weak_subjects].map((subject) => (
                  <tr
                    key={subject.subject_name}
                    className="border-t hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/subjects/${encodeURIComponent(subject.subject_name)}`)}
                  >
                    <td className="px-4 py-3 font-medium text-blue-600 hover:text-blue-800">{subject.subject_name}</td>
                    <td className="px-4 py-3 text-center">{subject.total_exams}</td>
                    <td className="px-4 py-3 text-center">{subject.average_net.toFixed(2)}</td>
                    <td className="px-4 py-3 text-center">{subject.best_net.toFixed(2)}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-1 rounded text-xs ${
                        subject.improvement_trend === 'improving' ? 'bg-green-100 text-green-700' :
                        subject.improvement_trend === 'declining' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {subject.improvement_trend === 'improving' ? '↑ Gelişiyor' :
                         subject.improvement_trend === 'declining' ? '↓ Düşüyor' :
                         '→ Stabil'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
