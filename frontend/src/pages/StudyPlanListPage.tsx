import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { studyPlansAPI } from '../api/client';
import type { StudyPlan } from '../types';

export default function StudyPlanListPage() {
  const navigate = useNavigate();

  const [plans, setPlans] = useState<StudyPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingPlanId, setDeletingPlanId] = useState<string | null>(null);

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await studyPlansAPI.list();
      setPlans(response.plans);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Planlar yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleArchivePlan = async (planId: string, planName: string) => {
    if (!confirm(`"${planName}" planını arşivlemek istediğinizden emin misiniz?`)) {
      return;
    }

    try {
      await studyPlansAPI.archive(planId);
      toast.success('Plan arşivlendi');
      await loadPlans(); // Reload list
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Plan arşivlenirken hata oluştu');
    }
  };

  const handleDeletePlan = async (planId: string, planName: string) => {
    if (!confirm(`"${planName}" planını kalıcı olarak silmek istediğinizden emin misiniz? Bu işlem geri alınamaz!`)) {
      return;
    }

    try {
      setDeletingPlanId(planId);
      await studyPlansAPI.delete(planId);
      toast.success('Plan silindi');
      await loadPlans(); // Reload list
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Plan silinirken hata oluştu');
    } finally {
      setDeletingPlanId(null);
    }
  };

  const calculateProgress = (plan: StudyPlan): number => {
    if (!plan.days || plan.days.length === 0) return 0;

    let totalItems = 0;
    let completedItems = 0;

    plan.days.forEach(day => {
      if (day.items) {
        totalItems += day.items.length;
        completedItems += day.items.filter(item => item.completed).length;
      }
    });

    return totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
  };

  const getStudyStyleLabel = (style: string): string => {
    const styles: Record<string, string> = {
      'intensive': 'Yoğun',
      'balanced': 'Dengeli',
      'relaxed': 'Rahat'
    };
    return styles[style] || style;
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Planlar yükleniyor...</p>
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
            onClick={loadPlans}
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
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2 text-sm sm:text-base"
          >
            ← Geri
          </button>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Çalışma Planları 📅
              </h1>
              <p className="text-sm sm:text-base text-gray-600 mt-1">
                {plans.length} plan bulundu
              </p>
            </div>
            <button
              onClick={() => navigate('/study-plan/create')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm sm:text-base font-medium whitespace-nowrap"
            >
              + Yeni Plan Oluştur
            </button>
          </div>
        </div>

        {/* Plans Grid */}
        {plans.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Henüz Plan Yok
            </h2>
            <p className="text-gray-600 mb-6">
              Çalışma planı oluşturarak önerilerinizi organize edebilir ve ilerlemenizi takip edebilirsiniz.
            </p>
            <button
              onClick={() => navigate('/study-plan/create')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              İlk Planını Oluştur
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {plans.map((plan) => {
              const progress = calculateProgress(plan);
              const isActive = plan.status === 'active';
              const isDeleting = deletingPlanId === plan.id;

              return (
                <div
                  key={plan.id}
                  className={`bg-white rounded-lg shadow-md p-4 border-2 transition-all hover:shadow-lg ${
                    isActive ? 'border-green-400' : 'border-gray-200'
                  }`}
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-gray-900 truncate">
                        {plan.name}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            isActive
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-600'
                          }`}
                        >
                          {isActive ? 'Aktif' : 'Arşiv'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {getStudyStyleLabel(plan.study_style)}
                        </span>
                      </div>
                    </div>

                    {/* Delete Button */}
                    <button
                      onClick={() => handleDeletePlan(plan.id, plan.name)}
                      disabled={isDeleting}
                      className="text-red-500 hover:text-red-700 p-1 disabled:opacity-50"
                      title="Planı Sil"
                    >
                      {isDeleting ? (
                        <div className="animate-spin h-5 w-5 border-2 border-red-500 border-t-transparent rounded-full"></div>
                      ) : (
                        <span className="text-xl">🗑️</span>
                      )}
                    </button>
                  </div>

                  {/* Date Range */}
                  <div className="text-sm text-gray-600 mb-3">
                    📅 {formatDate(plan.start_date)} - {formatDate(plan.end_date)}
                    <span className="mx-2">•</span>
                    {plan.time_frame} gün
                    <span className="mx-2">•</span>
                    {plan.daily_study_time} dk/gün
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">İlerleme</span>
                      <span className="font-bold text-gray-900">{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className={`h-2.5 rounded-full transition-all ${
                          progress >= 75 ? 'bg-green-500' :
                          progress >= 50 ? 'bg-yellow-500' :
                          progress >= 25 ? 'bg-orange-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {plan.days?.reduce((sum, day) => sum + (day.items?.filter(i => i.completed).length || 0), 0)} /
                      {plan.days?.reduce((sum, day) => sum + (day.items?.length || 0), 0)} görev tamamlandı
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/study-plan/${plan.id}`)}
                      className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      Görüntüle →
                    </button>
                    {isActive && (
                      <button
                        onClick={() => handleArchivePlan(plan.id, plan.name)}
                        className="bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors text-sm font-medium"
                        title="Arşivle"
                      >
                        📦
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
