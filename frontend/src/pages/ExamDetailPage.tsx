import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { examAPI } from '../api/client';
import type { ExamDetail } from '../types';

export const ExamDetailPage: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const [examDetail, setExamDetail] = useState<ExamDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (examId) {
      loadExamDetail(examId);
    }
  }, [examId]);

  const loadExamDetail = async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const detail = await examAPI.getExamDetail(id);
      setExamDetail(detail);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Sınav detayları yüklenirken bir hata oluştu');
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Detaylar yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error || !examDetail) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 p-6 rounded-lg max-w-md">
          <p className="text-red-700 font-medium">Hata</p>
          <p className="text-red-600 text-sm mt-2">{error || 'Sınav bulunamadı'}</p>
          <button
            onClick={() => navigate('/exams')}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            ← Sınav listesine dön
          </button>
        </div>
      </div>
    );
  }

  const { exam, student, overall_result, subject_results, learning_outcomes, questions } = examDetail;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <button
          onClick={() => navigate('/exams')}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium mb-6"
        >
          ← Sınav listesine dön
        </button>

        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{exam.exam_name}</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">
                <span className="font-medium">Öğrenci:</span> {student.name}
              </p>
              {student.school && (
                <p className="text-gray-600">
                  <span className="font-medium">Okul:</span> {student.school}
                </p>
              )}
              {student.grade && student.class_section && (
                <p className="text-gray-600">
                  <span className="font-medium">Sınıf:</span> {student.grade}/{student.class_section}
                </p>
              )}
            </div>
            <div>
              <p className="text-gray-600">
                <span className="font-medium">Sınav Tarihi:</span> {formatDate(exam.exam_date)}
              </p>
              {exam.booklet_type && (
                <p className="text-gray-600">
                  <span className="font-medium">Kitapçık:</span> {exam.booklet_type}
                </p>
              )}
              {exam.processed_at && (
                <p className="text-gray-600">
                  <span className="font-medium">İşlenme Tarihi:</span> {formatDate(exam.processed_at)}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Overall Results */}
        {overall_result && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Genel Sonuçlar</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Toplam Soru</p>
                <p className="text-2xl font-bold text-blue-600">{overall_result.total_questions}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Doğru</p>
                <p className="text-2xl font-bold text-green-600">{overall_result.total_correct}</p>
              </div>
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Yanlış</p>
                <p className="text-2xl font-bold text-red-600">{overall_result.total_wrong}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Boş</p>
                <p className="text-2xl font-bold text-gray-600">{overall_result.total_blank}</p>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Net</p>
                <p className="text-2xl font-bold text-purple-600">
                  {overall_result.net_score.toFixed(2)}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {overall_result.net_percentage.toFixed(1)}% başarı
                </p>
              </div>
              {overall_result.class_rank && overall_result.school_rank && (
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Sıralama</p>
                  <p className="text-lg font-bold text-yellow-600">
                    Sınıf: {overall_result.class_rank}/{overall_result.class_total}
                  </p>
                  <p className="text-lg font-bold text-yellow-600">
                    Okul: {overall_result.school_rank}/{overall_result.school_total}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Subject Results */}
        {subject_results.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Ders Bazında Sonuçlar</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium text-gray-700">Ders</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">Doğru</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">Yanlış</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">Boş</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">Net</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">Başarı</th>
                  </tr>
                </thead>
                <tbody>
                  {subject_results.map((subject) => (
                    <tr key={subject.id} className="border-t">
                      <td className="px-4 py-3 font-medium">{subject.subject_name}</td>
                      <td className="px-4 py-3 text-center text-green-600">{subject.correct}</td>
                      <td className="px-4 py-3 text-center text-red-600">{subject.wrong}</td>
                      <td className="px-4 py-3 text-center text-gray-600">{subject.blank}</td>
                      <td className="px-4 py-3 text-center font-bold">{subject.net_score.toFixed(2)}</td>
                      <td className="px-4 py-3 text-center">{subject.net_percentage.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Learning Outcomes */}
        {learning_outcomes.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Kazanım Analizi</h2>
            <div className="space-y-3">
              {learning_outcomes.map((outcome) => (
                <div key={outcome.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-medium text-gray-900">{outcome.subject_name}</p>
                      {outcome.outcome_description && (
                        <p className="text-sm text-gray-600">{outcome.outcome_description}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">
                        {outcome.acquired}/{outcome.total_questions}
                      </p>
                      {outcome.success_rate !== null && (
                        <p className="text-xs font-medium text-green-600">
                          %{outcome.success_rate.toFixed(0)} başarı
                        </p>
                      )}
                    </div>
                  </div>
                  {outcome.success_rate !== null && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${outcome.success_rate}%` }}
                      ></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Questions */}
        {questions.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Soru Detayları</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {questions.map((question) => (
                <div
                  key={question.id}
                  className={`border rounded-lg p-3 ${
                    question.is_correct
                      ? 'bg-green-50 border-green-200'
                      : question.is_blank
                      ? 'bg-gray-50 border-gray-200'
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-gray-700">{question.subject_name}</p>
                      <p className="text-xs text-gray-600">Soru #{question.question_number}</p>
                    </div>
                    <div className="text-right">
                      {question.is_correct && <span className="text-green-600 text-xl">✓</span>}
                      {!question.is_correct && !question.is_blank && <span className="text-red-600 text-xl">✗</span>}
                      {question.is_blank && <span className="text-gray-400 text-xl">−</span>}
                    </div>
                  </div>
                  <div className="mt-2 text-sm">
                    {question.correct_answer && (
                      <p className="text-gray-600">
                        Doğru: <span className="font-medium">{question.correct_answer}</span>
                      </p>
                    )}
                    {question.student_answer && (
                      <p className="text-gray-600">
                        Cevap: <span className="font-medium">{question.student_answer}</span>
                      </p>
                    )}
                    {question.is_blank && (
                      <p className="text-gray-500 italic">Boş bırakıldı</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
