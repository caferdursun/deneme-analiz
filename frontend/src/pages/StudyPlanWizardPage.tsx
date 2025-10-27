import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { studyPlansAPI } from '../api/client';
import { recommendationsAPI } from '../api/client';
import type { Recommendation, StudyPlanGenerateRequest } from '../types';

export default function StudyPlanWizardPage() {
  const navigate = useNavigate();

  // Wizard state
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form data
  const [planName, setPlanName] = useState('');
  const [timeFrame, setTimeFrame] = useState<number>(14);
  const [dailyStudyTime, setDailyStudyTime] = useState<number>(120);
  const [studyStyle, setStudyStyle] = useState<string>('balanced');
  const [selectedRecommendations, setSelectedRecommendations] = useState<string[]>([]);

  // Available recommendations
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(true);

  // Load recommendations on mount
  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoadingRecommendations(true);
      const data = await recommendationsAPI.getRecommendations();
      setRecommendations(data.recommendations.filter(r => r.is_active));
    } catch (err) {
      setError('Öneriler yüklenirken hata oluştu');
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const handleNext = () => {
    // Validate current step
    if (currentStep === 1 && !planName.trim()) {
      setError('Lütfen plan adı girin');
      return;
    }
    if (currentStep === 2 && selectedRecommendations.length === 0) {
      setError('En az bir konu seçmelisiniz');
      return;
    }

    setError(null);
    setCurrentStep(prev => Math.min(prev + 1, 5));
  };

  const handleBack = () => {
    setError(null);
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    const toastId = toast.loading('Çalışma planınız AI ile oluşturuluyor... Bu 10-15 saniye sürebilir.');

    try {
      setIsGenerating(true);
      setError(null);

      const request: StudyPlanGenerateRequest = {
        name: planName,
        time_frame: timeFrame,
        daily_study_time: dailyStudyTime,
        study_style: studyStyle,
        recommendation_ids: selectedRecommendations,
      };

      const plan = await studyPlansAPI.generate(request);

      toast.success('🎉 Çalışma planınız başarıyla oluşturuldu!', { id: toastId, duration: 3000 });

      // Navigate to study plan page after a brief delay to show success message
      setTimeout(() => {
        navigate(`/study-plan/${plan.id}`);
      }, 500);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Plan oluşturulurken hata oluştu';
      toast.error(errorMsg, { id: toastId });
      setError(errorMsg);
      setIsGenerating(false);
    }
  };

  const toggleRecommendation = (id: string) => {
    setSelectedRecommendations(prev =>
      prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]
    );
  };

  const selectAllRecommendations = () => {
    setSelectedRecommendations(recommendations.map(r => r.id));
  };

  const clearAllRecommendations = () => {
    setSelectedRecommendations([]);
  };

  // Subject color mapping
  const getSubjectColor = (subject: string | null): string => {
    const colors: { [key: string]: string } = {
      'Matematik': 'bg-blue-100 text-blue-700 border-blue-300',
      'Fizik': 'bg-purple-100 text-purple-700 border-purple-300',
      'Kimya': 'bg-green-100 text-green-700 border-green-300',
      'Biyoloji': 'bg-teal-100 text-teal-700 border-teal-300',
      'Türkçe': 'bg-red-100 text-red-700 border-red-300',
      'Geometri': 'bg-orange-100 text-orange-700 border-orange-300',
    };
    return subject ? (colors[subject] || 'bg-gray-100 text-gray-700 border-gray-300') : 'bg-gray-100 text-gray-700 border-gray-300';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Çalışma Planı Oluştur</h1>
          <p className="text-gray-600">Kişiselleştirilmiş çalışma planınızı oluşturun</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3, 4, 5].map((step) => (
              <div key={step} className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  step === currentStep ? 'bg-blue-600 text-white' :
                  step < currentStep ? 'bg-green-600 text-white' :
                  'bg-gray-300 text-gray-600'
                }`}>
                  {step < currentStep ? '✓' : step}
                </div>
                {step < 5 && (
                  <div className={`w-16 h-1 mx-2 ${
                    step < currentStep ? 'bg-green-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-600 w-20 text-center">Plan Adı</span>
            <span className="text-xs text-gray-600 w-20 text-center">Konular</span>
            <span className="text-xs text-gray-600 w-20 text-center">Süre</span>
            <span className="text-xs text-gray-600 w-20 text-center">Stil</span>
            <span className="text-xs text-gray-600 w-20 text-center">Önizleme</span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          {/* Step 1: Plan Name & Time Frame */}
          {currentStep === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Plan Adı ve Süre</h2>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Plan Adı <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={planName}
                  onChange={(e) => setPlanName(e.target.value)}
                  placeholder="Örn: 2 Haftalık Matematik Yoğunlaşma"
                  maxLength={100}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    planName.length > 0 && planName.length < 3
                      ? 'border-red-300 bg-red-50'
                      : planName.length >= 3
                      ? 'border-green-300 bg-green-50'
                      : 'border-gray-300'
                  }`}
                />
                <div className="mt-1 flex justify-between items-center">
                  {planName.length > 0 && planName.length < 3 && (
                    <p className="text-xs text-red-600">En az 3 karakter olmalı</p>
                  )}
                  {planName.length >= 3 && (
                    <p className="text-xs text-green-600">✓ Geçerli</p>
                  )}
                  <p className="text-xs text-gray-500 ml-auto">{planName.length}/100</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Plan Süresi
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {[
                    { value: 7, label: '1 Hafta', desc: 'Kısa vadeli hedefler için' },
                    { value: 14, label: '2 Hafta', desc: 'Dengeli bir çalışma için' },
                    { value: 30, label: '1 Ay', desc: 'Kapsamlı hazırlık için' },
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setTimeFrame(option.value)}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        timeFrame === option.value
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-300 hover:border-blue-300'
                      }`}
                    >
                      <div className="font-semibold text-gray-900 mb-1">{option.label}</div>
                      <div className="text-sm text-gray-600">{option.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Topic Selection */}
          {currentStep === 2 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Çalışılacak Konular</h2>
              <p className="text-gray-600 mb-6">
                Aktif önerilerinizden çalışma planınıza eklemek istediklerinizi seçin
              </p>

              <div className="flex justify-between items-center mb-4">
                <div className="text-sm text-gray-600">
                  {selectedRecommendations.length} / {recommendations.length} konu seçildi
                </div>
                <div className="space-x-2">
                  <button
                    onClick={selectAllRecommendations}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Hepsini Seç
                  </button>
                  <span className="text-gray-400">|</span>
                  <button
                    onClick={clearAllRecommendations}
                    className="text-sm text-gray-600 hover:text-gray-800 font-medium"
                  >
                    Temizle
                  </button>
                </div>
              </div>

              {loadingRecommendations ? (
                <div className="text-center py-8 text-gray-600">Öneriler yükleniyor...</div>
              ) : recommendations.length === 0 ? (
                <div className="text-center py-8 text-gray-600">
                  Aktif öneri bulunamadı. Önce sınavlarınızı yükleyin ve önerileri oluşturun.
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {recommendations.map((rec) => (
                    <label
                      key={rec.id}
                      className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        selectedRecommendations.includes(rec.id)
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-300 hover:border-blue-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedRecommendations.includes(rec.id)}
                        onChange={() => toggleRecommendation(rec.id)}
                        className="mt-1 mr-3 h-5 w-5 text-blue-600"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {rec.subject_name && (
                            <span className={`px-2 py-1 rounded text-xs font-semibold border ${getSubjectColor(rec.subject_name)}`}>
                              {rec.subject_name}
                            </span>
                          )}
                          <span className="px-2 py-1 rounded text-xs font-semibold bg-yellow-100 text-yellow-700 border border-yellow-300">
                            Öncelik: {rec.priority}
                          </span>
                        </div>
                        <div className="font-semibold text-gray-900 mb-1">
                          {rec.topic || 'Genel'}
                        </div>
                        <div className="text-sm text-gray-600">
                          {rec.description}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 3: Daily Study Time */}
          {currentStep === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Günlük Çalışma Süresi</h2>

              <div className="grid grid-cols-2 gap-4 mb-6">
                {[
                  { value: 60, label: '1 Saat', desc: 'Hafif tempo' },
                  { value: 120, label: '2 Saat', desc: 'Dengeli' },
                  { value: 180, label: '3 Saat', desc: 'Yoğun' },
                  { value: 240, label: '4 Saat', desc: 'Çok yoğun' },
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setDailyStudyTime(option.value)}
                    className={`p-4 border-2 rounded-lg text-left transition-all ${
                      dailyStudyTime === option.value
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-300 hover:border-blue-300'
                    }`}
                  >
                    <div className="font-semibold text-gray-900 mb-1">{option.label}</div>
                    <div className="text-sm text-gray-600">{option.desc}</div>
                  </button>
                ))}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Özel Süre (dakika)
                </label>
                <input
                  type="range"
                  min="30"
                  max="480"
                  step="30"
                  value={dailyStudyTime}
                  onChange={(e) => setDailyStudyTime(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="text-center text-sm text-gray-600 mt-2">
                  {dailyStudyTime} dakika ({Math.floor(dailyStudyTime / 60)} saat {dailyStudyTime % 60} dakika)
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Study Style */}
          {currentStep === 4 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Çalışma Tarzı</h2>

              <div className="space-y-4">
                {[
                  {
                    value: 'intensive',
                    label: 'Yoğun',
                    desc: '4+ saat/gün, minimal dinlenme, maksimum verimlilik',
                    icon: '⚡',
                  },
                  {
                    value: 'balanced',
                    label: 'Dengeli',
                    desc: '2-3 saat/gün, periyodik molalar, sürdürülebilir tempo',
                    icon: '⚖️',
                  },
                  {
                    value: 'relaxed',
                    label: 'Rahat',
                    desc: '1-2 saat/gün, bol tekrar, düşük stres',
                    icon: '🌱',
                  },
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setStudyStyle(option.value)}
                    className={`w-full p-6 border-2 rounded-lg text-left transition-all ${
                      studyStyle === option.value
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-300 hover:border-blue-300'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className="text-4xl">{option.icon}</div>
                      <div className="flex-1">
                        <div className="font-bold text-xl text-gray-900 mb-2">
                          {option.label}
                        </div>
                        <div className="text-gray-600">
                          {option.desc}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 5: Preview & Confirm */}
          {currentStep === 5 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Özet ve Onay</h2>

              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Plan Adı</div>
                  <div className="font-semibold text-gray-900">{planName}</div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Süre</div>
                    <div className="font-semibold text-gray-900">
                      {timeFrame === 7 ? '1 Hafta' : timeFrame === 14 ? '2 Hafta' : '1 Ay'}
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Günlük Çalışma</div>
                    <div className="font-semibold text-gray-900">
                      {Math.floor(dailyStudyTime / 60)}s {dailyStudyTime % 60}dk
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Çalışma Tarzı</div>
                    <div className="font-semibold text-gray-900 capitalize">
                      {studyStyle === 'intensive' ? 'Yoğun' : studyStyle === 'balanced' ? 'Dengeli' : 'Rahat'}
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-2">Seçilen Konular ({selectedRecommendations.length})</div>
                  <div className="space-y-2">
                    {recommendations
                      .filter(r => selectedRecommendations.includes(r.id))
                      .map(rec => (
                        <div key={rec.id} className="flex items-center gap-2">
                          {rec.subject_name && (
                            <span className={`px-2 py-1 rounded text-xs font-semibold border ${getSubjectColor(rec.subject_name)}`}>
                              {rec.subject_name}
                            </span>
                          )}
                          <span className="text-sm text-gray-900">{rec.topic}</span>
                        </div>
                      ))}
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-300 p-4 rounded-lg">
                  <div className="text-sm text-blue-800">
                    Bu bilgiler kullanılarak Claude AI ile kişiselleştirilmiş bir çalışma planı oluşturulacak.
                    Plan, konuları önceliklerine göre dengeli bir şekilde dağıtacak ve tekrar seansları içerecektir.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <button
            onClick={handleBack}
            disabled={currentStep === 1}
            className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Geri
          </button>

          {currentStep < 5 ? (
            <button
              onClick={handleNext}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
            >
              İleri
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isGenerating}
              className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isGenerating && (
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              )}
              {isGenerating ? 'Plan Oluşturuluyor...' : 'Plan Oluştur'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
