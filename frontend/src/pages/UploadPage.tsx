import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { examAPI } from '../api/client';
import type { ExamUploadResponse } from '../types';

export const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ExamUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
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

    try {
      const response = await examAPI.uploadExam(file);
      setResult(response);
      // Redirect to validation review page after 2 seconds
      setTimeout(() => {
        navigate(`/exams/${response.exam_id}/validate`);
      }, 2000);
    } catch (err: any) {
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
            <div className="mt-4 p-4 bg-blue-50 rounded-md">
              <p className="text-blue-700 text-sm">
                Sınav PDF'i analiz ediliyor... Bu işlem birkaç dakika sürebilir.
              </p>
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
