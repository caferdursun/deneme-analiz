import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { examAPI } from '../api/client';
import type { ExamUploadResponse } from '../types';

export const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ExamUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Lütfen bir PDF dosyası seçin');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);
    setProgress(0);

    // Simulate progress stages (5 stages, ~30 seconds each = ~150 seconds total)
    const stages = [
      { stage: 1, text: 'Temel veriler çıkartılıyor...', progress: 20, delay: 5000 },
      { stage: 2, text: 'Kazanımlar analiz ediliyor (1/2)...', progress: 40, delay: 30000 },
      { stage: 3, text: 'Kazanımlar analiz ediliyor (2/2)...', progress: 60, delay: 30000 },
      { stage: 4, text: 'Sorular işleniyor (1/2)...', progress: 80, delay: 30000 },
      { stage: 5, text: 'Sorular işleniyor (2/2)...', progress: 95, delay: 30000 },
    ];

    let currentStageIndex = 0;
    const progressInterval = setInterval(() => {
      if (currentStageIndex < stages.length) {
        const stage = stages[currentStageIndex];
        setCurrentStage(stage.text);
        setProgress(stage.progress);
        currentStageIndex++;
      }
    }, 30000); // Update every 30 seconds

    // Set initial stage immediately
    setCurrentStage(stages[0].text);
    setProgress(5);

    try {
      const response = await examAPI.uploadExam(file);
      clearInterval(progressInterval);
      setProgress(100);
      setCurrentStage('Tamamlandı!');
      setResult(response);

      // Redirect to validation review page after 2 seconds
      setTimeout(() => {
        navigate(`/exams/${response.exam_id}/validate`);
      }, 2000);
    } catch (err: any) {
      clearInterval(progressInterval);
      setError(err.response?.data?.detail || 'Dosya yüklenirken bir hata oluştu');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Sınav PDF'i Yükle</h1>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sınav PDF Dosyası
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={uploading}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          {file && (
            <div className="mb-6">
              <p className="text-sm text-gray-600">
                Seçili dosya: <span className="font-medium">{file.name}</span>
              </p>
              <p className="text-sm text-gray-500">
                Boyut: {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700
              disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {uploading ? 'Yükleniyor...' : 'Yükle ve Analiz Et'}
          </button>

          {uploading && (
            <div className="mt-6 space-y-4">
              {/* Progress Bar */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">{currentStage}</span>
                  <span className="text-sm font-medium text-gray-700">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>

              {/* Stage Info */}
              <div className="p-4 bg-blue-50 rounded-md border border-blue-200">
                <p className="text-blue-900 text-sm font-medium mb-2">
                  📊 Claude AI ile 5 Aşamalı Analiz
                </p>
                <ul className="text-blue-700 text-xs space-y-1">
                  <li className={progress >= 20 ? 'line-through opacity-60' : ''}>
                    ✓ Aşama 1: Temel veriler (öğrenci, sınav, genel sonuçlar)
                  </li>
                  <li className={progress >= 40 ? 'line-through opacity-60' : progress >= 20 ? 'font-semibold' : ''}>
                    ⏳ Aşama 2: Kazanımlar - İlk yarı
                  </li>
                  <li className={progress >= 60 ? 'line-through opacity-60' : progress >= 40 ? 'font-semibold' : ''}>
                    ⏳ Aşama 3: Kazanımlar - İkinci yarı
                  </li>
                  <li className={progress >= 80 ? 'line-through opacity-60' : progress >= 60 ? 'font-semibold' : ''}>
                    ⏳ Aşama 4: Sorular - İlk yarı
                  </li>
                  <li className={progress >= 95 ? 'line-through opacity-60' : progress >= 80 ? 'font-semibold' : ''}>
                    ⏳ Aşama 5: Sorular - İkinci yarı
                  </li>
                </ul>
                <p className="text-blue-600 text-xs mt-3">
                  ⏱️ Tahmini süre: ~2.5 dakika | Lütfen bekleyin...
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 rounded-md">
              <p className="text-red-700 text-sm font-medium">Hata</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {result && (
            <div className="mt-4 p-4 bg-green-50 rounded-md">
              <p className="text-green-700 text-sm font-medium mb-2">Başarılı!</p>
              <p className="text-green-600 text-sm mb-2">{result.message}</p>

              {result.validation_report && (
                <div className="mt-3 p-3 bg-white rounded border border-green-200">
                  <p className="text-sm font-medium text-gray-700 mb-1">
                    Doğrulama Durumu: {result.validation_report.status}
                  </p>
                  <p className="text-xs text-gray-600">
                    {result.validation_report.summary}
                  </p>
                  {result.validation_report.errors > 0 && (
                    <p className="text-xs text-red-600 mt-1">
                      ⚠ {result.validation_report.errors} kritik hata bulundu
                    </p>
                  )}
                  {result.validation_report.warnings > 0 && (
                    <p className="text-xs text-yellow-600 mt-1">
                      ⚠ {result.validation_report.warnings} uyarı bulundu
                    </p>
                  )}
                </div>
              )}

              <p className="text-green-600 text-xs mt-2">
                Doğrulama sayfasına yönlendiriliyorsunuz...
              </p>
            </div>
          )}
        </div>

        <div className="mt-6">
          <button
            onClick={() => navigate('/exams')}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            ← Sınav listesine dön
          </button>
        </div>
      </div>
    </div>
  );
};
