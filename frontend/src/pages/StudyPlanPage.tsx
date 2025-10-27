import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { studyPlansAPI } from '../api/client';
import type { StudyPlan, StudyPlanDay, StudyPlanItem, StudyPlanProgress } from '../types';

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

  const loadPlan = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await studyPlansAPI.getById(planId!);
      setPlan(data);

      // Select first day by default
      if (data.days && data.days.length > 0) {
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

      // Update local state
      setPlan(prevPlan => {
        if (!prevPlan) return null;

        return {
          ...prevPlan,
          days: prevPlan.days.map(day => ({
            ...day,
            items: day.items.map(i =>
              i.id === item.id ? { ...i, completed: newCompleted, completed_at: newCompleted ? new Date().toISOString() : null } : i
            ),
            completed: day.items.every(i => i.id === item.id ? newCompleted : i.completed)
          }))
        };
      });

      // Update selected day
      if (selectedDay && selectedDay.id === item.day_id) {
        setSelectedDay(prevDay => {
          if (!prevDay) return null;
          return {
            ...prevDay,
            items: prevDay.items.map(i =>
              i.id === item.id ? { ...i, completed: newCompleted, completed_at: newCompleted ? new Date().toISOString() : null } : i
            ),
            completed: prevDay.items.every(i => i.id === item.id ? newCompleted : i.completed)
          };
        });
      }

      // Reload progress
      await loadProgress();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'İşlem tamamlanırken hata oluştu');
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
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Yükleniyor...</div>
      </div>
    );
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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
          >
            ← Geri
          </button>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{plan.name}</h1>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>{new Date(plan.start_date).toLocaleDateString('tr-TR')} - {new Date(plan.end_date).toLocaleDateString('tr-TR')}</span>
                  <span>•</span>
                  <span>{plan.time_frame} gün</span>
                  <span>•</span>
                  <span>{plan.daily_study_time} dakika/gün</span>
                  <span>•</span>
                  <span className="capitalize">
                    {plan.study_style === 'intensive' ? 'Yoğun' : plan.study_style === 'balanced' ? 'Dengeli' : 'Rahat'}
                  </span>
                </div>
              </div>

              <div className={`px-4 py-2 rounded-lg font-semibold ${
                plan.status === 'active' ? 'bg-green-100 text-green-700' :
                plan.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {plan.status === 'active' ? 'Aktif' : plan.status === 'completed' ? 'Tamamlandı' : 'Arşivlendi'}
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Calendar Grid */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Günlük Plan</h2>

              <div className="grid grid-cols-7 gap-2">
                {plan.days.map((day) => {
                  const today = isToday(day.date);
                  const past = isPast(day.date);
                  const selected = selectedDay?.id === day.id;

                  return (
                    <button
                      key={day.id}
                      onClick={() => setSelectedDay(day)}
                      className={`p-3 rounded-lg border-2 transition-all text-center ${
                        selected
                          ? 'border-blue-600 bg-blue-50'
                          : today
                          ? 'border-green-600 bg-green-50'
                          : day.completed
                          ? 'border-green-300 bg-green-50'
                          : past
                          ? 'border-gray-200 bg-gray-50 opacity-60'
                          : 'border-gray-300 hover:border-blue-300'
                      }`}
                    >
                      <div className={`text-xs mb-1 ${selected ? 'text-blue-700' : today ? 'text-green-700' : 'text-gray-600'}`}>
                        {formatDate(day.date)}
                      </div>
                      <div className={`text-lg font-bold ${selected ? 'text-blue-900' : today ? 'text-green-900' : 'text-gray-900'}`}>
                        {day.day_number}
                      </div>
                      {day.completed && (
                        <div className="text-green-600 mt-1">✓</div>
                      )}
                      {today && !day.completed && (
                        <div className="text-xs text-green-700 mt-1 font-semibold">Bugün</div>
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
              <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Gün {selectedDay.day_number}</h3>
                    <div className="text-sm text-gray-600">{new Date(selectedDay.date).toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
                  </div>
                  {selectedDay.completed && (
                    <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
                      Tamamlandı
                    </div>
                  )}
                </div>

                <div className="mb-4">
                  <div className="text-sm text-gray-600">Toplam Süre</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {Math.floor(selectedDay.total_duration_minutes / 60)}s {selectedDay.total_duration_minutes % 60}dk
                  </div>
                </div>

                <div className="space-y-3">
                  {selectedDay.items.map((item) => (
                    <div
                      key={item.id}
                      className={`p-4 border-2 rounded-lg ${
                        item.completed ? 'border-green-300 bg-green-50' : 'border-gray-300'
                      }`}
                    >
                      <label className="flex items-start gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={item.completed}
                          onChange={() => handleItemToggle(item)}
                          className="mt-1 h-5 w-5 text-green-600"
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2 py-1 rounded text-xs font-semibold border ${getSubjectColor(item.subject_name)}`}>
                              {item.subject_name}
                            </span>
                            <span className="text-xs text-gray-600">{item.duration_minutes} dk</span>
                          </div>
                          <div className={`font-semibold mb-1 ${item.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                            {item.topic}
                          </div>
                          {item.description && (
                            <div className={`text-sm ${item.completed ? 'text-gray-400' : 'text-gray-600'}`}>
                              {item.description}
                            </div>
                          )}
                          {item.completed && item.completed_at && (
                            <div className="text-xs text-green-600 mt-2">
                              ✓ {new Date(item.completed_at).toLocaleString('tr-TR')}
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
