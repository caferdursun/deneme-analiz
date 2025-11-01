import { useState, useEffect } from 'react';
import axios from 'axios';
import { ChevronRight, ChevronDown, BookOpen, FileText, List } from 'lucide-react';

interface Topic {
  id: string;
  name: string;
  grade_info: string | null;
  order: number;
}

interface Subject {
  id: string;
  name: string;
  order: number;
  topics: Topic[];
}

interface ExamType {
  id: string;
  name: string;
  display_name: string;
  order: number;
  subjects: Subject[];
}

interface CurriculumData {
  exam_types: ExamType[];
  total_exam_types: number;
  total_subjects: number;
  total_topics: number;
}

export function CurriculumPage() {
  const [curriculum, setCurriculum] = useState<CurriculumData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Expanded state tracking
  const [expandedExamTypes, setExpandedExamTypes] = useState<Set<string>>(new Set());
  const [expandedSubjects, setExpandedSubjects] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchCurriculum();
  }, []);

  const fetchCurriculum = async () => {
    try {
      setLoading(true);
      const response = await axios.get<CurriculumData>('/api/curriculum');
      setCurriculum(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching curriculum:', err);
      setError(err.response?.data?.detail || 'Müfredat yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const toggleExamType = (examTypeId: string) => {
    const newExpanded = new Set(expandedExamTypes);
    if (newExpanded.has(examTypeId)) {
      newExpanded.delete(examTypeId);
    } else {
      newExpanded.add(examTypeId);
    }
    setExpandedExamTypes(newExpanded);
  };

  const toggleSubject = (subjectId: string) => {
    const newExpanded = new Set(expandedSubjects);
    if (newExpanded.has(subjectId)) {
      newExpanded.delete(subjectId);
    } else {
      newExpanded.add(subjectId);
    }
    setExpandedSubjects(newExpanded);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Müfredat yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md">
          <div className="text-red-600 text-center">
            <p className="font-semibold mb-2">Hata</p>
            <p className="text-sm">{error}</p>
          </div>
          <button
            onClick={fetchCurriculum}
            className="mt-4 w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Tekrar Dene
          </button>
        </div>
      </div>
    );
  }

  if (!curriculum) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Müfredat bulunamadı</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Müfredat</h1>
              <p className="mt-2 text-sm text-gray-600">
                YKS sınav müfredatı - Sınav türü, ders ve konular
              </p>
            </div>
            <div className="flex gap-4 text-sm">
              <div className="bg-blue-50 px-4 py-2 rounded-lg">
                <span className="text-blue-600 font-semibold">{curriculum.total_exam_types}</span>
                <span className="text-gray-600 ml-1">Sınav Türü</span>
              </div>
              <div className="bg-green-50 px-4 py-2 rounded-lg">
                <span className="text-green-600 font-semibold">{curriculum.total_subjects}</span>
                <span className="text-gray-600 ml-1">Ders</span>
              </div>
              <div className="bg-purple-50 px-4 py-2 rounded-lg">
                <span className="text-purple-600 font-semibold">{curriculum.total_topics}</span>
                <span className="text-gray-600 ml-1">Konu</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-4">
          {curriculum.exam_types.map((examType) => (
            <div key={examType.id} className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Exam Type Header */}
              <button
                onClick={() => toggleExamType(examType.id)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <BookOpen className="w-5 h-5 text-blue-600" />
                  <div className="text-left">
                    <h2 className="text-lg font-semibold text-gray-900">
                      {examType.name}
                    </h2>
                    <p className="text-sm text-gray-600">{examType.display_name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-500">
                    {examType.subjects.length} ders
                  </span>
                  {expandedExamTypes.has(examType.id) ? (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </button>

              {/* Subjects */}
              {expandedExamTypes.has(examType.id) && (
                <div className="border-t border-gray-200">
                  {examType.subjects.map((subject) => (
                    <div key={subject.id} className="border-b border-gray-100 last:border-b-0">
                      {/* Subject Header */}
                      <button
                        onClick={() => toggleSubject(subject.id)}
                        className="w-full px-8 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="w-4 h-4 text-green-600" />
                          <h3 className="font-medium text-gray-900">{subject.name}</h3>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-sm text-gray-500">
                            {subject.topics.length} konu
                          </span>
                          {expandedSubjects.has(subject.id) ? (
                            <ChevronDown className="w-4 h-4 text-gray-400" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-gray-400" />
                          )}
                        </div>
                      </button>

                      {/* Topics */}
                      {expandedSubjects.has(subject.id) && (
                        <div className="bg-gray-50 px-10 py-3">
                          <div className="space-y-2">
                            {subject.topics.map((topic, index) => (
                              <div
                                key={topic.id}
                                className="flex items-start gap-3 py-2 px-3 bg-white rounded border border-gray-200"
                              >
                                <List className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm text-gray-900">
                                    <span className="text-gray-500 font-mono mr-2">
                                      {String(index + 1).padStart(2, '0')}.
                                    </span>
                                    {topic.name}
                                  </p>
                                  {topic.grade_info && (
                                    <p className="text-xs text-gray-500 mt-1">
                                      Sınıf: {topic.grade_info}
                                    </p>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default CurriculumPage;
