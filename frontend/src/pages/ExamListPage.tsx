import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { examAPI } from '../api/client';
import type { Exam } from '../types';

export const ExamListPage: React.FC = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadExams();
  }, []);

  const loadExams = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await examAPI.getExams();
      setExams(response.exams);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Sınavlar yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const handleDelete = async (examId: string) => {
    if (!confirm('Bu sınavı silmek istediğinizden emin misiniz?')) {
      return;
    }

    try {
      await examAPI.deleteExam(examId);
      setExams(exams.filter(exam => exam.id !== examId));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Sınav silinirken bir hata oluştu');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Sınavlar yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 p-6 rounded-lg max-w-md">
          <p className="text-red-700 font-medium">Hata</p>
          <p className="text-red-600 text-sm mt-2">{error}</p>
          <button
            onClick={loadExams}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Tekrar dene
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Sınavlarım</h1>
          <button
            onClick={() => navigate('/upload')}
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors font-medium"
          >
            + Yeni Sınav Ekle
          </button>
        </div>

        {exams.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <p className="text-gray-500 text-lg mb-4">Henüz sınav eklenmemiş</p>
            <button
              onClick={() => navigate('/upload')}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              İlk sınavı ekle →
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {exams.map((exam) => (
              <div
                key={exam.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">
                      {exam.exam_name}
                    </h2>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p>
                        <span className="font-medium">Tarih:</span>{' '}
                        {formatDate(exam.exam_date)}
                      </p>
                      {exam.booklet_type && (
                        <p>
                          <span className="font-medium">Kitapçık:</span>{' '}
                          {exam.booklet_type}
                        </p>
                      )}
                      {exam.processed_at && (
                        <p>
                          <span className="font-medium">İşlenme:</span>{' '}
                          {formatDate(exam.processed_at)}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => navigate(`/exams/${exam.id}`)}
                      className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      Detay
                    </button>
                    <button
                      onClick={() => handleDelete(exam.id)}
                      className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors text-sm font-medium"
                    >
                      Sil
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 text-center text-gray-500 text-sm">
          Toplam {exams.length} sınav
        </div>
      </div>
    </div>
  );
};
