import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsAPI, recommendationsAPI, examAPI, studyPlansAPI } from '../api/client';
import type { AnalyticsOverview, Recommendation, StudyPlan, StudyPlanItem } from '../types';
import { DashboardSkeleton } from '../components/Skeleton';

export const DashboardPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [allRecommendations, setAllRecommendations] = useState<Recommendation[]>([]); // All recs for flag matching
  const [pendingCount, setPendingCount] = useState(0);
  const [newRecommendationsCount, setNewRecommendationsCount] = useState(0);
  const [activePlan, setActivePlan] = useState<StudyPlan | null>(null);
  const [todayTasks, setTodayTasks] = useState<StudyPlanItem[]>([]);
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
      const [analyticsData, recommendationsData, pendingData] = await Promise.all([
        analyticsAPI.getOverview(),
        recommendationsAPI.getRecommendations().catch(() => ({ recommendations: [], total: 0 })),
        examAPI.getPendingCount().catch(() => ({ pending_count: 0 }))
      ]);
      setAnalytics(analyticsData);
      setAllRecommendations(recommendationsData.recommendations); // Store all for flag matching
      setRecommendations(recommendationsData.recommendations.slice(0, 3)); // Top 3 for display
      setPendingCount(pendingData.pending_count);

      // Calculate new/updated recommendations count for badge
      const newUpdatedCount = recommendationsData.recommendations.filter(
        (r: Recommendation) => r.status === 'new' || r.status === 'updated'
      ).length;
      setNewRecommendationsCount(newUpdatedCount);

      // Load active study plan and today's tasks
      try {
        const plan = await studyPlansAPI.getActive();
        setActivePlan(plan);

        // Find today's tasks
        const today = new Date().toISOString().split('T')[0];
        const todayDay = plan.days.find(day => day.date === today);
        if (todayDay) {
          setTodayTasks(todayDay.items);
        }
      } catch (err) {
        // No active plan is fine, just don't set it
        setActivePlan(null);
        setTodayTasks([]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analytics yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <DashboardSkeleton />;
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

  // MF program subjects (Matematik-Fen)
  const MF_SUBJECTS = ['Türkçe', 'Matematik', 'Geometri', 'Fizik', 'Kimya', 'Biyoloji'];

  // Filter subjects for MF program
  const mfSubjects = top_subjects.filter(subject => MF_SUBJECTS.includes(subject.subject_name));
  const topMfSubjects = mfSubjects.slice(0, 3); // Top 3 MF subjects
  const weakMfSubjects = mfSubjects.slice(-3).reverse(); // Bottom 3 MF subjects

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

  const getPriorityColor = (priority: number): string => {
    if (priority === 1) return 'border-red-500 bg-red-50';
    if (priority === 2) return 'border-orange-500 bg-orange-50';
    if (priority === 3) return 'border-yellow-500 bg-yellow-50';
    return 'border-gray-300 bg-gray-50';
  };

  const getPriorityLabel = (priority: number): string => {
    if (priority === 1) return 'Çok Önemli';
    if (priority === 2) return 'Önemli';
    if (priority === 3) return 'Orta';
    return 'Düşük';
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

  const getSubjectColor = (subject: string): string => {
    const colors: { [key: string]: string } = {
      'Matematik': 'bg-blue-100 text-blue-700 border-blue-300',
      'Fizik': 'bg-purple-100 text-purple-700 border-purple-300',
      'Kimya': 'bg-green-100 text-green-700 border-green-300',
      'Biyoloji': 'bg-teal-100 text-teal-700 border-teal-300',
      'Türkçe': 'bg-red-100 text-red-700 border-red-300',
      'Geometri': 'bg-orange-100 text-orange-700 border-orange-300',
    };
    return colors[subject] || 'bg-gray-100 text-gray-700 border-gray-300';
  };

  const handleTaskToggle = async (item: StudyPlanItem) => {
    if (!activePlan) return;

    try {
      const newCompleted = !item.completed;
      await studyPlansAPI.updateItemCompletion(activePlan.id, item.id, newCompleted);

      // Update local state
      setTodayTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === item.id ? { ...task, completed: newCompleted } : task
        )
      );
    } catch (err) {
      console.error('Task toggle hatası:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-4 sm:py-8 px-3 sm:px-4">
      <div className="max-w-7xl mx-auto">
        {/* Mobile-optimized header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h1>

          {/* Mobile: 2x3 grid, Desktop: horizontal */}
          <div className="grid grid-cols-2 sm:flex gap-2 sm:gap-3">
            <button
              onClick={() => navigate('/upload')}
              className="bg-blue-600 text-white py-2 px-3 sm:px-4 rounded-md hover:bg-blue-700 text-xs sm:text-sm font-medium whitespace-nowrap"
            >
              + Sınav
            </button>
            <button
              onClick={() => navigate('/exams')}
              className="bg-gray-600 text-white py-2 px-3 sm:px-4 rounded-md hover:bg-gray-700 text-xs sm:text-sm font-medium relative whitespace-nowrap"
            >
              Sınavlar
              {pendingCount > 0 && (
                <span className="absolute -top-1 sm:-top-2 -right-1 sm:-right-2 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 sm:w-6 sm:h-6 flex items-center justify-center animate-pulse">
                  {pendingCount}
                </span>
              )}
            </button>
            <button
              onClick={() => navigate('/learning-outcomes/tree')}
              className="bg-purple-600 text-white py-2 px-3 sm:px-4 rounded-md hover:bg-purple-700 text-xs sm:text-sm font-medium whitespace-nowrap"
            >
              🌳 Konu Ağacı
            </button>
            <button
              onClick={() => navigate('/recommendations')}
              className="bg-green-600 text-white py-2 px-3 sm:px-4 rounded-md hover:bg-green-700 text-xs sm:text-sm font-medium relative whitespace-nowrap"
            >
              Öneriler
              {newRecommendationsCount > 0 && (
                <span className="absolute -top-1 sm:-top-2 -right-1 sm:-right-2 bg-yellow-400 text-gray-900 text-xs font-bold rounded-full w-5 h-5 sm:w-6 sm:h-6 flex items-center justify-center animate-pulse">
                  {newRecommendationsCount}
                </span>
              )}
            </button>
            <button
              onClick={() => navigate('/study-plans')}
              className="bg-indigo-600 text-white py-2 px-3 sm:px-4 rounded-md hover:bg-indigo-700 text-xs sm:text-sm font-medium col-span-2 sm:col-span-1 whitespace-nowrap"
            >
              📅 Çalışma Planları
            </button>
          </div>
        </div>

        {/* Stats Cards - Mobile: 2 columns, Desktop: 4 columns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <p className="text-xs sm:text-sm text-gray-600 mb-1">Toplam Sınav</p>
            <p className="text-2xl sm:text-3xl font-bold text-blue-600">{stats.total_exams}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <p className="text-xs sm:text-sm text-gray-600 mb-1">Son Net</p>
            <p className="text-2xl sm:text-3xl font-bold text-green-600">
              {stats.latest_net_score?.toFixed(2) || '-'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <p className="text-xs sm:text-sm text-gray-600 mb-1">Ortalama Net</p>
            <p className="text-2xl sm:text-3xl font-bold text-purple-600">
              {stats.average_net_score?.toFixed(2) || '-'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <p className="text-xs sm:text-sm text-gray-600 mb-1">Doğruluk Oranı</p>
            <p className="text-2xl sm:text-3xl font-bold text-yellow-600">
              {stats.overall_accuracy ? `%${stats.overall_accuracy.toFixed(1)}` : '-'}
            </p>
          </div>
        </div>

        {/* Recommendations Section */}
        {recommendations.length > 0 && (
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg shadow-lg p-4 sm:p-6 mb-6 sm:mb-8 border-l-4 border-green-500">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="text-xl sm:text-2xl">💡</div>
                <div>
                  <h2 className="text-lg sm:text-xl font-bold text-gray-900">Sizin İçin Öneriler</h2>
                  <p className="text-xs text-gray-600 mt-0.5">
                    {allRecommendations.length} aktif öneri
                    {newRecommendationsCount > 0 && (
                      <span className="ml-2 text-green-600 font-semibold">
                        ({newRecommendationsCount} yeni)
                      </span>
                    )}
                  </p>
                </div>
              </div>
              <button
                onClick={() => navigate('/recommendations')}
                className="text-xs sm:text-sm font-medium text-blue-600 hover:text-blue-800 whitespace-nowrap"
              >
                Tümü →
              </button>
            </div>

            <div className="space-y-4">
              {recommendations.map((rec) => (
                <div
                  key={rec.id}
                  className={`bg-white rounded-lg p-4 border-l-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer ${getPriorityColor(rec.priority)}`}
                  onClick={() => navigate('/recommendations')}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        {/* Status Badge */}
                        <span className={`px-2 py-1 rounded text-xs font-bold border ${getStatusBadge(rec.status).color}`}>
                          {getStatusBadge(rec.status).label}
                        </span>
                        {/* Priority Badge */}
                        <span className="text-xs font-semibold px-2 py-1 rounded bg-white border">
                          {getPriorityLabel(rec.priority)}
                        </span>
                        {rec.subject_name && (
                          <span className="text-xs font-medium text-gray-700">
                            {rec.subject_name}
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-semibold text-gray-900 mb-1">{rec.description}</p>
                      {rec.action_items && rec.action_items.length > 0 && (
                        <p className="text-xs text-gray-600">
                          {rec.action_items[0]}
                        </p>
                      )}
                    </div>
                    {rec.impact_score && (
                      <div className="ml-4 text-center">
                        <div className="text-lg font-bold text-green-600">{rec.impact_score.toFixed(1)}</div>
                        <div className="text-xs text-gray-500">Etki</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Today's Tasks Section */}
        {todayTasks.length > 0 && (
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg shadow-lg p-4 sm:p-6 mb-6 sm:mb-8 border-l-4 border-indigo-500">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="text-xl sm:text-2xl">📅</div>
                <div>
                  <h2 className="text-lg sm:text-xl font-bold text-gray-900">Bugünün Görevleri</h2>
                  <p className="text-xs text-gray-600 mt-0.5">
                    {todayTasks.filter(t => t.completed).length} / {todayTasks.length} tamamlandı
                  </p>
                </div>
              </div>
              <button
                onClick={() => navigate(`/study-plan/${activePlan!.id}`)}
                className="text-xs sm:text-sm font-medium text-blue-600 hover:text-blue-800 whitespace-nowrap"
              >
                Tümü →
              </button>
            </div>

            <div className="space-y-3">
              {todayTasks.map((task) => (
                <div
                  key={task.id}
                  className={`bg-white rounded-lg p-4 border-2 ${
                    task.completed ? 'border-green-300 bg-green-50' : 'border-gray-300'
                  }`}
                >
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => handleTaskToggle(task)}
                      className="mt-1 h-5 w-5 text-green-600"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-semibold border ${getSubjectColor(task.subject_name)}`}>
                          {task.subject_name}
                        </span>
                        <span className="text-xs text-gray-600">{task.duration_minutes} dk</span>
                      </div>
                      <div className={`font-semibold mb-1 ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                        {task.topic}
                      </div>
                      {task.description && (
                        <div className={`text-sm ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
                          {task.description}
                        </div>
                      )}
                    </div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Score Trend Chart */}
        {formattedScoreTrends.length > 0 && (
          <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 sm:mb-8">
            <h2 className="text-lg sm:text-xl font-bold mb-4">Başarı Oranı Gelişimi (%)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formattedScoreTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="short_name" height={60} tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
                          <p className="text-sm font-medium mb-1">{data.exam_name}</p>
                          <p className="text-sm text-blue-600">Başarı: %{data.net_percentage.toFixed(2)}</p>
                          <p className="text-sm text-gray-500">Net: {data.net_score}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="net_percentage" stroke="#3b82f6" name="Başarı %" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Subject Performance */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
          {/* Top Subjects - Show top 3 MF subjects for chart */}
          {topMfSubjects.length > 0 && (
            <div className="bg-white rounded-lg shadow p-4 sm:p-6">
              <h2 className="text-lg sm:text-xl font-bold mb-4 text-green-600">En İyi 3 Ders (MF)</h2>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={topMfSubjects}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="subject_name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="average_percentage" fill="#10b981" name="Ortalama %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Weak Subjects - Show bottom 3 MF subjects */}
          {weakMfSubjects.length > 0 && (
            <div className="bg-white rounded-lg shadow p-4 sm:p-6">
              <h2 className="text-lg sm:text-xl font-bold mb-4 text-red-600">Gelişmesi Gereken 3 Ders (MF)</h2>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={weakMfSubjects}>
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

        {/* Subject Details Table - All Subjects */}
        <div className="bg-white rounded-lg shadow p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-bold mb-4">Tüm Dersler ({top_subjects.length})</h2>
          <div className="overflow-x-auto -mx-4 sm:mx-0">
            <table className="w-full text-xs sm:text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-2 sm:px-4 py-2 text-left">Ders</th>
                  <th className="px-2 sm:px-4 py-2 text-center hidden sm:table-cell">Sınav</th>
                  <th className="px-2 sm:px-4 py-2 text-center">Ort. Net</th>
                  <th className="px-2 sm:px-4 py-2 text-center">Ort. %</th>
                  <th className="px-2 sm:px-4 py-2 text-center hidden md:table-cell">En İyi</th>
                  <th className="px-2 sm:px-4 py-2 text-center hidden lg:table-cell">Trend</th>
                </tr>
              </thead>
              <tbody>
                {top_subjects.map((subject) => {
                  // Count active recommendations for this subject
                  const subjectRecommendations = allRecommendations.filter(r => r.subject_name === subject.subject_name);
                  const recommendationCount = subjectRecommendations.length;
                  const hasRecommendation = recommendationCount > 0;
                  const isMfSubject = MF_SUBJECTS.includes(subject.subject_name);
                  return (
                    <tr
                      key={subject.subject_name}
                      className={`border-t cursor-pointer ${
                        isMfSubject
                          ? 'bg-blue-50 hover:bg-blue-100'
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => navigate(`/subjects/${encodeURIComponent(subject.subject_name)}`)}
                    >
                      <td className="px-2 sm:px-4 py-3">
                        <div className="flex items-center gap-1 sm:gap-2 flex-wrap">
                          <span className="font-medium text-blue-600 hover:text-blue-800 text-xs sm:text-sm">{subject.subject_name}</span>
                          {hasRecommendation && (
                            <span className="text-xs px-1.5 sm:px-2 py-0.5 bg-green-100 text-green-700 rounded-full border border-green-300">
                              💡 {recommendationCount}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-2 sm:px-4 py-3 text-center hidden sm:table-cell">{subject.total_exams}</td>
                      <td className="px-2 sm:px-4 py-3 text-center">{subject.average_net.toFixed(2)}</td>
                      <td className="px-2 sm:px-4 py-3 text-center">{subject.average_percentage.toFixed(1)}%</td>
                      <td className="px-2 sm:px-4 py-3 text-center hidden md:table-cell">{subject.best_net.toFixed(2)}</td>
                      <td className="px-2 sm:px-4 py-3 text-center hidden lg:table-cell">
                        <span className={`px-2 py-1 rounded text-xs ${
                          subject.improvement_trend === 'improving' ? 'bg-green-100 text-green-700' :
                          subject.improvement_trend === 'declining' ? 'bg-red-100 text-red-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {subject.improvement_trend === 'improving' ? '↑' :
                           subject.improvement_trend === 'declining' ? '↓' :
                           '→'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
