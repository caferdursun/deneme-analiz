import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { examAPI } from '../api/client';
import type { ExamDetail, ValidationReport } from '../types';

export const ValidationReviewPage: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();
  const [exam, setExam] = useState<ExamDetail | null>(null);
  const [validationReport, setValidationReport] = useState<ValidationReport | null>(null);
  const [selectedSource, setSelectedSource] = useState<'claude' | 'local'>('claude');
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTooltip, setShowTooltip] = useState<string | null>(null);

  useEffect(() => {
    loadExamData();
  }, [examId]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (loading || confirming) return;

      // C for Claude
      if (e.key.toLowerCase() === 'c' && !e.ctrlKey && !e.metaKey) {
        setSelectedSource('claude');
      }
      // L for Local
      else if (e.key.toLowerCase() === 'l' && !e.ctrlKey && !e.metaKey) {
        setSelectedSource('local');
      }
      // Enter to confirm
      else if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey) {
        handleConfirm();
      }
      // Escape to cancel
      else if (e.key === 'Escape') {
        navigate('/exams');
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [loading, confirming, selectedSource, examId]);

  const loadExamData = async () => {
    if (!examId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await examAPI.getExamDetail(examId);
      setExam(data);

      // Parse validation report
      if (data.exam.validation_report) {
        const report = JSON.parse(data.exam.validation_report);
        setValidationReport(report);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Sınav bilgileri yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!examId) return;

    try {
      setConfirming(true);
      setError(null);

      await examAPI.confirmExam(examId, selectedSource);

      // Redirect to exam detail page
      navigate(`/exams/${examId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Sınav onaylanırken hata oluştu');
    } finally {
      setConfirming(false);
    }
  };

  const handleReviewLater = () => {
    // Just go back to exams list, exam will remain in pending_confirmation status
    navigate('/exams');
  };

  const getStatusBadge = (status: string) => {
    if (status === 'passed') return 'bg-green-100 text-green-800';
    if (status === 'warning') return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getSeverityBadge = (severity: string) => {
    if (severity === 'error') return 'bg-red-100 text-red-800';
    if (severity === 'warning') return 'bg-yellow-100 text-yellow-800';
    return 'bg-blue-100 text-blue-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Doğrulama raporu yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error || !exam || !validationReport) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 p-6 rounded-lg max-w-md">
          <p className="text-red-700 font-medium">Hata</p>
          <p className="text-red-600 text-sm mt-2">{error || 'Sınav bulunamadı'}</p>
          <button
            onClick={() => navigate('/exams')}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Sınavlara dön
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Sınav Doğrulama</h1>
          <p className="text-gray-600 mt-2">{exam.exam.exam_name}</p>
        </div>

        {/* Validation Report Summary */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Doğrulama Raporu</h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(validationReport.status)}`}>
              {validationReport.status === 'passed' ? 'Başarılı' :
               validationReport.status === 'warning' ? 'Uyarı' : 'Hata'}
            </span>
          </div>

          <p className="text-gray-600 mb-4">{validationReport.summary}</p>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-600">Toplam Sorun</p>
              <p className="text-2xl font-bold text-gray-900">{validationReport.total_issues}</p>
            </div>
            <div className="bg-red-50 p-4 rounded">
              <p className="text-sm text-red-600">Hatalar</p>
              <p className="text-2xl font-bold text-red-900">{validationReport.errors}</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded">
              <p className="text-sm text-yellow-600">Uyarılar</p>
              <p className="text-2xl font-bold text-yellow-900">{validationReport.warnings}</p>
            </div>
          </div>
        </div>

        {/* Validation Issues */}
        {validationReport.issues && validationReport.issues.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Sorunlar</h2>
            <div className="space-y-3">
              {validationReport.issues.map((issue, index) => (
                <div
                  key={index}
                  className="border-l-4 border-gray-300 pl-4 py-2"
                  style={{ borderColor: issue.severity === 'error' ? '#ef4444' : '#f59e0b' }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityBadge(issue.severity)}`}>
                      {issue.severity === 'error' ? 'Hata' : 'Uyarı'}
                    </span>
                    <span className="font-medium text-gray-900">{issue.field}</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Claude:</span> {JSON.stringify(issue.claude_value)}
                    {' | '}
                    <span className="font-medium">Local:</span> {JSON.stringify(issue.local_value)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Keyboard Shortcuts Help */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800 font-medium mb-2">Klavye Kısayolları:</p>
          <div className="grid grid-cols-2 gap-2 text-xs text-blue-700">
            <div><kbd className="px-2 py-1 bg-white rounded border border-blue-300">C</kbd> - Claude seç</div>
            <div><kbd className="px-2 py-1 bg-white rounded border border-blue-300">L</kbd> - Local seç</div>
            <div><kbd className="px-2 py-1 bg-white rounded border border-blue-300">Enter</kbd> - Onayla</div>
            <div><kbd className="px-2 py-1 bg-white rounded border border-blue-300">Esc</kbd> - İptal</div>
          </div>
        </div>

        {/* Data Source Selection */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Veri Kaynağını Seç</h2>
            <div
              className="relative"
              onMouseEnter={() => setShowTooltip('source-help')}
              onMouseLeave={() => setShowTooltip(null)}
            >
              <span className="text-gray-400 hover:text-gray-600 cursor-help text-xl">ⓘ</span>
              {showTooltip === 'source-help' && (
                <div className="absolute z-10 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg -left-60 top-0">
                  <p className="font-medium mb-1">Claude AI:</p>
                  <p className="mb-2">Yapay zeka ile gelişmiş analiz. Learning outcomes ve detaylı bilgileri daha iyi çıkarır.</p>
                  <p className="font-medium mb-1">Local Parser:</p>
                  <p>Temel PDF okuma. Hızlıdır ama daha az detay içerir.</p>
                </div>
              )}
            </div>
          </div>
          <p className="text-gray-600 mb-4">
            Sınav verileri iki farklı kaynaktan alındı. Lütfen kullanmak istediğiniz veri kaynağını seçin:
          </p>

          <div className="space-y-3">
            <button
              onClick={() => setSelectedSource('claude')}
              className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                selectedSource === 'claude'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    selectedSource === 'claude' ? 'border-blue-500' : 'border-gray-300'
                  }`}>
                    {selectedSource === 'claude' && (
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Claude AI</p>
                    <p className="text-sm text-gray-600">Yapay zeka ile detaylı analiz (Önerilen)</p>
                  </div>
                </div>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600 border border-gray-300">C</kbd>
              </div>
            </button>

            <button
              onClick={() => setSelectedSource('local')}
              className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                selectedSource === 'local'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    selectedSource === 'local' ? 'border-blue-500' : 'border-gray-300'
                  }`}>
                    {selectedSource === 'local' && (
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Yerel Parser</p>
                    <p className="text-sm text-gray-600">Temel PDF okuma</p>
                  </div>
                </div>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600 border border-gray-300">L</kbd>
              </div>
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-3">
          <button
            onClick={() => navigate('/exams')}
            className="bg-gray-200 text-gray-700 py-3 rounded-md hover:bg-gray-300 font-medium"
            disabled={confirming}
          >
            İptal
          </button>
          <button
            onClick={handleReviewLater}
            className="bg-yellow-500 text-white py-3 rounded-md hover:bg-yellow-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={confirming}
            title="Sınavı onaylamadan geri dön. Daha sonra inceleyebilirsin."
          >
            Sonra İncele
          </button>
          <button
            onClick={handleConfirm}
            className="bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={confirming}
          >
            {confirming ? 'Onaylanıyor...' : 'Onayla ✓'}
          </button>
        </div>
        <p className="text-xs text-gray-500 text-center mt-2">
          Onaylanmamış sınavlar 24 saat sonra otomatik olarak silinecektir.
        </p>
      </div>
    </div>
  );
};
