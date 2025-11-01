import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { curriculumAPI } from '../api/client';
import type { CurriculumFull, CurriculumSubject, CurriculumGrade, CurriculumUnit, CurriculumTopic } from '../types';

export const CurriculumPage: React.FC = () => {
  const [curriculum, setCurriculum] = useState<CurriculumFull | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Expandable state - now Subject->Grade->Unit hierarchy
  const [expandedSubjects, setExpandedSubjects] = useState<Set<string>>(new Set());
  const [expandedGrades, setExpandedGrades] = useState<Set<string>>(new Set());
  const [expandedUnits, setExpandedUnits] = useState<Set<string>>(new Set());

  const navigate = useNavigate();

  useEffect(() => {
    loadCurriculum();
  }, []);

  const loadCurriculum = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await curriculumAPI.getAll();
      setCurriculum(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Müfredat yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const toggleSubject = (subjectId: string) => {
    const newExpanded = new Set(expandedSubjects);
    if (newExpanded.has(subjectId)) {
      newExpanded.delete(subjectId);
      // Also collapse all grades and units in this subject
      const newExpandedGrades = new Set(expandedGrades);
      const newExpandedUnits = new Set(expandedUnits);
      expandedGrades.forEach(gradeId => {
        if (gradeId.startsWith(subjectId)) {
          newExpandedGrades.delete(gradeId);
        }
      });
      expandedUnits.forEach(unitId => {
        if (unitId.startsWith(subjectId)) {
          newExpandedUnits.delete(unitId);
        }
      });
      setExpandedGrades(newExpandedGrades);
      setExpandedUnits(newExpandedUnits);
    } else {
      newExpanded.add(subjectId);
    }
    setExpandedSubjects(newExpanded);
  };

  const toggleGrade = (gradeId: string) => {
    const newExpanded = new Set(expandedGrades);
    if (newExpanded.has(gradeId)) {
      newExpanded.delete(gradeId);
      // Also collapse all units in this grade
      const newExpandedUnits = new Set(expandedUnits);
      expandedUnits.forEach(unitId => {
        if (unitId.startsWith(gradeId)) {
          newExpandedUnits.delete(unitId);
        }
      });
      setExpandedUnits(newExpandedUnits);
    } else {
      newExpanded.add(gradeId);
    }
    setExpandedGrades(newExpanded);
  };

  const toggleUnit = (unitId: string) => {
    const newExpanded = new Set(expandedUnits);
    if (newExpanded.has(unitId)) {
      newExpanded.delete(unitId);
    } else {
      newExpanded.add(unitId);
    }
    setExpandedUnits(newExpanded);
  };

  const getSubjectColor = (subject: string): string => {
    const colors: { [key: string]: string } = {
      'Türkçe': 'bg-red-50 border-red-200 hover:border-red-300',
      'Türk Dili ve Edebiyatı': 'bg-red-50 border-red-200 hover:border-red-300',
      'Matematik': 'bg-blue-50 border-blue-200 hover:border-blue-300',
      'Fizik': 'bg-purple-50 border-purple-200 hover:border-purple-300',
      'Kimya': 'bg-green-50 border-green-200 hover:border-green-300',
      'Biyoloji': 'bg-teal-50 border-teal-200 hover:border-teal-300',
      'Geometri': 'bg-orange-50 border-orange-200 hover:border-orange-300',
      'Tarih': 'bg-amber-50 border-amber-200 hover:border-amber-300',
      'Coğrafya': 'bg-emerald-50 border-emerald-200 hover:border-emerald-300',
    };
    return colors[subject] || 'bg-gray-50 border-gray-200 hover:border-gray-300';
  };

  const getSubjectIcon = (subject: string): string => {
    const icons: { [key: string]: string } = {
      'Türkçe': '📚',
      'Türk Dili ve Edebiyatı': '📚',
      'Matematik': '🔢',
      'Fizik': '⚛️',
      'Kimya': '🧪',
      'Biyoloji': '🧬',
      'Geometri': '📐',
      'Tarih': '🏛️',
      'Coğrafya': '🗺️',
    };
    return icons[subject] || '📖';
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

  if (error || !curriculum) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-red-50 p-6 rounded-lg max-w-md w-full">
          <p className="text-red-700 font-medium">Hata</p>
          <p className="text-red-600 text-sm mt-2">{error || 'Veri bulunamadı'}</p>
          <button
            onClick={loadCurriculum}
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
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Lise Müfredatı</h1>
            <p className="text-sm text-gray-600 mt-1">
              {curriculum.total_subjects} ders • {curriculum.total_units} ünite • {curriculum.total_topics} konu
            </p>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 text-sm font-medium self-start sm:self-auto"
          >
            ← Dashboard
          </button>
        </div>

        {/* Curriculum Content - Subject -> Grade -> Unit -> Topic */}
        <div className="space-y-3">
          {curriculum.subjects.map((subject: CurriculumSubject) => {
            const isSubjectExpanded = expandedSubjects.has(subject.id);

            return (
              <div key={subject.id} className="bg-white rounded-lg shadow-sm overflow-hidden">
                {/* Subject Header (Level 1: Ders) */}
                <button
                  onClick={() => toggleSubject(subject.id)}
                  className={`w-full text-left px-4 py-4 border-2 transition-colors ${getSubjectColor(subject.subject_name)}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{getSubjectIcon(subject.subject_name)}</span>
                      <div>
                        <h2 className="text-lg font-bold text-gray-900">{subject.subject_name}</h2>
                        <p className="text-sm text-gray-600">
                          {subject.grades.length} sınıf •{' '}
                          {subject.grades.reduce((acc, g) => acc + g.units.length, 0)} ünite •{' '}
                          {subject.grades.reduce((acc, g) => acc + g.units.reduce((sum, u) => sum + u.topics.length, 0), 0)} konu
                        </p>
                      </div>
                    </div>
                    <svg
                      className={`w-5 h-5 text-gray-500 transition-transform ${isSubjectExpanded ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                {/* Grades (Level 2: Sınıf) */}
                {isSubjectExpanded && (
                  <div className="px-4 py-3 space-y-2 bg-gray-50">
                    {subject.grades.map((grade: CurriculumGrade) => {
                      const isGradeExpanded = expandedGrades.has(grade.id);

                      return (
                        <div key={grade.id} className="bg-white rounded-md border border-gray-200">
                          {/* Grade Header */}
                          <button
                            onClick={() => toggleGrade(grade.id)}
                            className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-bold text-indigo-600 bg-indigo-100 px-2 py-1 rounded">
                                  {grade.grade}. Sınıf
                                </span>
                                <span className="text-sm text-gray-700 font-medium">{subject.subject_name}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-gray-500">
                                  {grade.units.length} ünite • {grade.units.reduce((sum, u) => sum + u.topics.length, 0)} konu
                                </span>
                                <svg
                                  className={`w-4 h-4 text-gray-400 transition-transform ${isGradeExpanded ? 'rotate-180' : ''}`}
                                  fill="none"
                                  stroke="currentColor"
                                  viewBox="0 0 24 24"
                                >
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                              </div>
                            </div>
                          </button>

                          {/* Units (Level 3: Ünite) */}
                          {isGradeExpanded && (
                            <div className="px-4 pb-3 space-y-2">
                              {grade.units.map((unit: CurriculumUnit) => {
                                const isUnitExpanded = expandedUnits.has(unit.id);

                                return (
                                  <div key={unit.id} className="bg-gray-50 rounded border border-gray-200">
                                    {/* Unit Header */}
                                    <button
                                      onClick={() => toggleUnit(unit.id)}
                                      className="w-full text-left px-3 py-2 hover:bg-gray-100 transition-colors"
                                    >
                                      <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                          <span className="text-xs font-bold text-blue-600 bg-blue-100 px-2 py-1 rounded">
                                            Ünite {unit.unit_no}
                                          </span>
                                          <span className="text-sm font-semibold text-gray-800">{unit.unit_name}</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                          <span className="text-xs text-gray-500">{unit.topics.length} konu</span>
                                          <svg
                                            className={`w-4 h-4 text-gray-400 transition-transform ${isUnitExpanded ? 'rotate-180' : ''}`}
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                          >
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                          </svg>
                                        </div>
                                      </div>
                                    </button>

                                    {/* Topics (Level 4: Konu) */}
                                    {isUnitExpanded && (
                                      <div className="px-3 pb-2">
                                        <ul className="space-y-1">
                                          {unit.topics.map((topic: CurriculumTopic) => (
                                            <li key={topic.id} className="text-sm text-gray-700 py-2 px-3 hover:bg-white rounded flex items-start gap-2">
                                              <span className="text-gray-400 mt-0.5">•</span>
                                              <span>{topic.topic_name}</span>
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default CurriculumPage;
