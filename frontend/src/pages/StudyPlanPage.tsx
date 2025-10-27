import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { studyPlansAPI } from '../api/client';
import type { StudyPlan, StudyPlanDay, StudyPlanItem, StudyPlanProgress } from '../types';
import { StudyPlanSkeleton } from '../components/Skeleton';

export default function StudyPlanPage() {
  const { planId } = useParams<{ planId: string }>();
  const navigate = useNavigate();

  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [progress, setProgress] = useState<StudyPlanProgress | null>(null);
  const [selectedDay, setSelectedDay] = useState<StudyPlanDay | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (planId) {
      loadPlan();
      loadProgress();
    }
  }, [planId]);

  const loadPlan = async (preserveSelectedDay: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      const data = await studyPlansAPI.getById(planId!);
      setPlan(data);

      // Update selected day with fresh data or select first day
      if (preserveSelectedDay && selectedDay) {
        // Find the same day in the fresh data
        const updatedDay = data.days.find(d => d.id === selectedDay.id);
        if (updatedDay) {
          setSelectedDay(updatedDay);
        }
      } else if (data.days && data.days.length > 0 && !selectedDay) {
        // Only select first day if no day is selected yet
        setSelectedDay(data.days[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Plan yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const loadProgress = async () => {
    try {
      const progressData = await studyPlansAPI.getProgress(planId!);
      setProgress(progressData);
    } catch (err) {
      console.error('Progress yüklenirken hata:', err);
    }
  };

  const handleItemToggle = async (item: StudyPlanItem) => {
    if (!plan) return;

    try {
      const newCompleted = !item.completed;
      await studyPlansAPI.updateItemCompletion(plan.id, item.id, newCompleted);

      // Reload plan data from backend to ensure consistency
      // Pass true to preserve the currently selected day
      await loadPlan(true);
      await loadProgress();

      // Show success toast
      if (newCompleted) {
        toast.success('✓ Görev tamamlandı!', { duration: 2000 });
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'İşlem tamamlanırken hata oluştu');
    }
  };

  const handleArchivePlan = async () => {
    if (!plan || !confirm('Bu planı arşivlemek istediğinizden emin misiniz? Arşivlenen planlar aktif olmaktan çıkar.')) return;

    const toastId = toast.loading('Plan arşivleniyor...');
    try {
      await studyPlansAPI.archive(plan.id);
      toast.success('Plan başarıyla arşivlendi!', { id: toastId });
      navigate('/dashboard');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Plan arşivlenirken hata oluştu', { id: toastId });
    }
  };

  const handleDeletePlan = async () => {
    if (!plan || !confirm('Bu planı kalıcı olarak silmek istediğinizden emin misiniz? Bu işlem geri alınamaz!')) return;

    const toastId = toast.loading('Plan siliniyor...');
    try {
      await studyPlansAPI.delete(plan.id);
      toast.success('Plan başarıyla silindi!', { id: toastId });
      navigate('/dashboard');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Plan silinirken hata oluştu', { id: toastId });
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

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const days = ['Paz', 'Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt'];
    return `${days[date.getDay()]} ${date.getDate()}`;
  };

  const isToday = (dateStr: string): boolean => {
    const date = new Date(dateStr);
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isPast = (dateStr: string): boolean => {
    const date = new Date(dateStr);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };

  if (loading) {
    return <StudyPlanSkeleton />;
  }

  if (error || !plan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md">
          <div className="text-red-600 mb-4">{error || 'Plan bulunamadı'}</div>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Ana Sayfaya Dön
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
      <div className="max-w-7xl mx-auto px-3 sm:px-4">
        {/* Header */}
        <div className="mb-4 sm:mb-6">
          <button
            onClick={() => navigate('/study-plans')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2 text-sm sm:text-base"
          >
            ← Tüm Planlar
          </button>

          <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-4">
              <div className="flex-1">
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-2">{plan.name}</h1>
                <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-600">
                  <span className="whitespace-nowrap">{new Date(plan.start_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })} - {new Date(plan.end_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}</span>
                  <span className="hidden sm:inline">•</span>
                  <span>{plan.time_frame} gün</span>
                  <span className="hidden sm:inline">•</span>
                  <span>{plan.daily_study_time} dk/gün</span>
                  <span className="hidden sm:inline">•</span>
                  <span className="capitalize">
                    {plan.study_style === 'intensive' ? 'Yoğun' : plan.study_style === 'balanced' ? 'Dengeli' : 'Rahat'}
                  </span>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
                <div className={`px-3 py-2 rounded-lg font-semibold text-center text-sm ${
                  plan.status === 'active' ? 'bg-green-100 text-green-700' :
                  plan.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {plan.status === 'active' ? 'Aktif' : plan.status === 'completed' ? 'Tamamlandı' : 'Arşivlendi'}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <button
                    onClick={() => navigate('/study-plan/create')}
                    className="flex-1 sm:flex-none px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs sm:text-sm font-medium whitespace-nowrap"
                    title="Yeni plan oluştur"
                  >
                    + Plan
                  </button>

                  {plan.status === 'active' && (
                    <button
                      onClick={handleArchivePlan}
                      className="flex-1 sm:flex-none px-3 sm:px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-xs sm:text-sm font-medium whitespace-nowrap"
                      title="Planı arşivle"
                    >
                      📦
                    </button>
                  )}

                  <button
                    onClick={handleDeletePlan}
                    className="flex-1 sm:flex-none px-3 sm:px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-xs sm:text-sm font-medium whitespace-nowrap"
                    title="Planı sil"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            {progress && (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">İlerleme</span>
                  <span className="text-sm font-semibold text-gray-900">{progress.completion_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                  <div
                    className={`h-3 rounded-full transition-all ${
                      progress.on_track ? 'bg-green-600' : 'bg-yellow-600'
                    }`}
                    style={{ width: `${progress.completion_percentage}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-600">
                  <span>{progress.completed_items} / {progress.total_items} görev tamamlandı</span>
                  <span>{progress.days_remaining} gün kaldı</span>
                </div>
                {!progress.on_track && (
                  <div className="mt-2 text-xs text-yellow-700 bg-yellow-50 px-3 py-2 rounded">
                    ⚠️ Hedef ilerlemenin biraz gerisinde kalmışsınız
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Calendar Grid */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Günlük Plan</h2>

              {/* Mobile: 4 columns, Desktop: 7 columns */}
              <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-7 gap-1.5 sm:gap-2">
                {plan.days.map((day) => {
                  const today = isToday(day.date);
                  const past = isPast(day.date);
                  const selected = selectedDay?.id === day.id;

                  // Calculate completion progress
                  const completedCount = day.items.filter(item => item.completed).length;
                  const totalCount = day.items.length;
                  const isPartiallyCompleted = completedCount > 0 && completedCount < totalCount;
                  const completionPercentage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

                  return (
                    <button
                      key={day.id}
                      onClick={() => setSelectedDay(day)}
                      className={`p-2 sm:p-3 rounded-lg border-2 transition-all text-center relative ${
                        selected
                          ? 'border-blue-600 bg-blue-50'
                          : today
                          ? 'border-green-600 bg-green-50'
                          : day.completed
                          ? 'border-green-300 bg-green-50'
                          : isPartiallyCompleted
                          ? 'border-yellow-300 bg-yellow-50'
                          : past
                          ? 'border-gray-200 bg-gray-50 opacity-60'
                          : 'border-gray-300 hover:border-blue-300'
                      }`}
                    >
                      <div className={`text-xs mb-1 hidden sm:block ${selected ? 'text-blue-700' : today ? 'text-green-700' : 'text-gray-600'}`}>
                        {formatDate(day.date)}
                      </div>
                      <div className={`text-base sm:text-lg font-bold ${selected ? 'text-blue-900' : today ? 'text-green-900' : 'text-gray-900'}`}>
                        {day.day_number}
                      </div>

                      {/* Completion indicator */}
                      {day.completed && (
                        <div className="text-green-600 mt-0.5 sm:mt-1 text-base sm:text-lg">✓</div>
                      )}
                      {isPartiallyCompleted && (
                        <div className="mt-0.5 sm:mt-1">
                          <div className="text-xs text-yellow-700 font-semibold">{completedCount}/{totalCount}</div>
                          <div className="w-full bg-yellow-200 rounded-full h-1 mt-0.5 sm:mt-1">
                            <div
                              className="bg-yellow-600 h-1 rounded-full transition-all"
                              style={{ width: `${completionPercentage}%` }}
                            />
                          </div>
                        </div>
                      )}
                      {today && !day.completed && !isPartiallyCompleted && (
                        <div className="text-xs text-green-700 mt-0.5 sm:mt-1 font-semibold hidden sm:block">Bugün</div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Day Detail Card */}
          <div className="lg:col-span-1">
            {selectedDay ? (
              <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 lg:sticky lg:top-8">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900">Gün {selectedDay.day_number}</h3>
                    <div className="text-xs sm:text-sm text-gray-600">{new Date(selectedDay.date).toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
                  </div>
                  {selectedDay.completed && (
                    <div className="bg-green-100 text-green-700 px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-semibold">
                      Tamamlandı
                    </div>
                  )}
                </div>

                <div className="mb-4">
                  <div className="text-xs sm:text-sm text-gray-600">Toplam Süre</div>
                  <div className="text-base sm:text-lg font-semibold text-gray-900">
                    {Math.floor(selectedDay.total_duration_minutes / 60)}s {selectedDay.total_duration_minutes % 60}dk
                  </div>
                </div>

                <div className="space-y-2 sm:space-y-3">
                  {selectedDay.items.map((item) => (
                    <div
                      key={item.id}
                      className={`p-3 sm:p-4 border-2 rounded-lg ${
                        item.completed ? 'border-green-300 bg-green-50' : 'border-gray-300'
                      }`}
                    >
                      <label className="flex items-start gap-2 sm:gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={item.completed}
                          onChange={() => handleItemToggle(item)}
                          className="mt-1 h-4 w-4 sm:h-5 sm:w-5 text-green-600 flex-shrink-0"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2 flex-wrap">
                            <span className={`px-2 py-1 rounded text-xs font-semibold border ${getSubjectColor(item.subject_name)}`}>
                              {item.subject_name}
                            </span>
                            <span className="text-xs text-gray-600 whitespace-nowrap">{item.duration_minutes} dk</span>
                          </div>
                          <div className={`text-sm sm:text-base font-semibold mb-1 ${item.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                            {item.topic}
                          </div>
                          {item.description && (
                            <div className={`text-xs sm:text-sm ${item.completed ? 'text-gray-400' : 'text-gray-600'}`}>
                              {item.description}
                            </div>
                          )}
                          {item.completed && item.completed_at && (
                            <div className="text-xs text-green-600 mt-2">
                              ✓ {new Date(item.completed_at).toLocaleString('tr-TR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                            </div>
                          )}
                        </div>
                      </label>
                    </div>
                  ))}
                </div>

                {selectedDay.notes && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-300 rounded-lg">
                    <div className="text-sm font-semibold text-gray-700 mb-1">Notlar</div>
                    <div className="text-sm text-gray-600">{selectedDay.notes}</div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-600">
                Detayları görmek için bir gün seçin
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
