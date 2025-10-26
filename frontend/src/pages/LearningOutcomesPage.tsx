import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyticsAPI } from '../api/client';
import type { LearningOutcomeStats } from '../types';

// Group statistics interface
interface GroupStats {
  totalOutcomes: number;
  totalAppearances: number;
  totalQuestions: number;
  totalAcquired: number;
  averageSuccessRate: number;
}

// Hierarchical group interfaces
interface SubcategoryGroup {
  subcategory: string;
  stats: GroupStats;
  outcomes: LearningOutcomeStats[];
}

interface CategoryGroup {
  category: string;
  stats: GroupStats;
  subcategories: SubcategoryGroup[];
}

interface SubjectGroup {
  subject: string;
  stats: GroupStats;
  categories: CategoryGroup[];
}

interface StatusGroup {
  status: 'excellent' | 'good' | 'medium' | 'weak';
  label: string;
  stats: GroupStats;
  subjects: SubjectGroup[];
}

export const LearningOutcomesPage: React.FC = () => {
  const [allOutcomes, setAllOutcomes] = useState<LearningOutcomeStats[]>([]);
  const [groupedData, setGroupedData] = useState<StatusGroup[]>([]);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadAllLearningOutcomes();
  }, []);

  const loadAllLearningOutcomes = async () => {
    try {
      setLoading(true);
      setError(null);

      const outcomes = await analyticsAPI.getAllLearningOutcomes();
      setAllOutcomes(outcomes);

      // Group data hierarchically
      const grouped = groupOutcomesByStatus(outcomes);
      setGroupedData(grouped);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kazanımlar yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Calculate group statistics
  const calculateStats = (outcomes: LearningOutcomeStats[]): GroupStats => {
    const totalOutcomes = outcomes.length;
    const totalAppearances = outcomes.reduce((sum, o) => sum + o.total_appearances, 0);
    const totalQuestions = outcomes.reduce((sum, o) => sum + o.total_questions, 0);
    const totalAcquired = outcomes.reduce((sum, o) => sum + o.total_acquired, 0);
    const averageSuccessRate = totalOutcomes > 0
      ? outcomes.reduce((sum, o) => sum + o.average_success_rate, 0) / totalOutcomes
      : 0;

    return {
      totalOutcomes,
      totalAppearances,
      totalQuestions,
      totalAcquired,
      averageSuccessRate,
    };
  };

  // Group outcomes by status (Çok İyi, İyi, Orta, Zayıf)
  const groupOutcomesByStatus = (outcomes: LearningOutcomeStats[]): StatusGroup[] => {
    const statuses = [
      { status: 'excellent' as const, label: 'Çok İyi (≥80%)', min: 80 },
      { status: 'good' as const, label: 'İyi (60-80%)', min: 60, max: 80 },
      { status: 'medium' as const, label: 'Orta (40-60%)', min: 40, max: 60 },
      { status: 'weak' as const, label: 'Zayıf (<40%)', min: 0, max: 40 },
    ];

    return statuses.map(({ status, label, min, max }) => {
      const statusOutcomes = outcomes.filter(o => {
        if (status === 'excellent') {
          return o.average_success_rate >= min; // >= 80%, includes 100%
        }
        return o.average_success_rate >= min && o.average_success_rate < max!;
      });

      return {
        status,
        label,
        stats: calculateStats(statusOutcomes),
        subjects: groupBySubject(statusOutcomes),
      };
    });
  };

  // Group by subject
  const groupBySubject = (outcomes: LearningOutcomeStats[]): SubjectGroup[] => {
    const subjectMap = new Map<string, LearningOutcomeStats[]>();

    outcomes.forEach(outcome => {
      const subject = outcome.subject_name;
      if (!subjectMap.has(subject)) {
        subjectMap.set(subject, []);
      }
      subjectMap.get(subject)!.push(outcome);
    });

    return Array.from(subjectMap.entries()).map(([subject, subjectOutcomes]) => ({
      subject,
      stats: calculateStats(subjectOutcomes),
      categories: groupByCategory(subjectOutcomes),
    }));
  };

  // Group by category
  const groupByCategory = (outcomes: LearningOutcomeStats[]): CategoryGroup[] => {
    const categoryMap = new Map<string, LearningOutcomeStats[]>();

    outcomes.forEach(outcome => {
      const category = outcome.category || 'Kategorisiz';
      if (!categoryMap.has(category)) {
        categoryMap.set(category, []);
      }
      categoryMap.get(category)!.push(outcome);
    });

    return Array.from(categoryMap.entries()).map(([category, categoryOutcomes]) => ({
      category,
      stats: calculateStats(categoryOutcomes),
      subcategories: groupBySubcategory(categoryOutcomes),
    }));
  };

  // Group by subcategory
  const groupBySubcategory = (outcomes: LearningOutcomeStats[]): SubcategoryGroup[] => {
    const subcategoryMap = new Map<string, LearningOutcomeStats[]>();

    outcomes.forEach(outcome => {
      const subcategory = outcome.subcategory || 'Alt Kategorisiz';
      if (!subcategoryMap.has(subcategory)) {
        subcategoryMap.set(subcategory, []);
      }
      subcategoryMap.get(subcategory)!.push(outcome);
    });

    return Array.from(subcategoryMap.entries()).map(([subcategory, subcategoryOutcomes]) => ({
      subcategory,
      stats: calculateStats(subcategoryOutcomes),
      outcomes: subcategoryOutcomes,
    }));
  };

  // Toggle group expansion
  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev);
      if (next.has(groupId)) {
        next.delete(groupId);
      } else {
        next.add(groupId);
      }
      return next;
    });
  };

  // Expand/collapse all
  const toggleAll = () => {
    if (expandedGroups.size > 0) {
      setExpandedGroups(new Set());
    } else {
      // Expand all groups
      const allGroupIds: string[] = [];
      groupedData.forEach(status => {
        allGroupIds.push(`status-${status.status}`);
        status.subjects.forEach(subject => {
          allGroupIds.push(`subject-${status.status}-${subject.subject}`);
          subject.categories.forEach(category => {
            allGroupIds.push(`category-${status.status}-${subject.subject}-${category.category}`);
            category.subcategories.forEach(subcategory => {
              allGroupIds.push(`subcategory-${status.status}-${subject.subject}-${category.category}-${subcategory.subcategory}`);
            });
          });
        });
      });
      setExpandedGroups(new Set(allGroupIds));
    }
  };

  // Get status color
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'excellent': return 'bg-green-50 border-green-300';
      case 'good': return 'bg-blue-50 border-blue-300';
      case 'medium': return 'bg-yellow-50 border-yellow-300';
      case 'weak': return 'bg-red-50 border-red-300';
      default: return 'bg-gray-50 border-gray-300';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'excellent': return '🟢';
      case 'good': return '🔵';
      case 'medium': return '🟡';
      case 'weak': return '🔴';
      default: return '⚪';
    }
  };

  const getSuccessRateColor = (rate: number): string => {
    if (rate >= 80) return 'bg-green-500';
    if (rate >= 60) return 'bg-blue-500';
    if (rate >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Kazanımlar yükleniyor...</p>
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
            onClick={() => navigate('/dashboard')}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            ← Dashboard'a Dön
          </button>
        </div>
      </div>
    );
  }

  const totalStats = calculateStats(allOutcomes);

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Geri
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Kazanımlar (Öğrenme Çıktıları)</h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleAll}
              className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors text-sm font-medium"
            >
              {expandedGroups.size > 0 ? '📥 Tümünü Kapat' : '📤 Tümünü Aç'}
            </button>
            <button
              onClick={() => navigate('/learning-outcomes/cleanup')}
              className="bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors text-sm font-medium"
            >
              🧹 Kazanımları Temizle
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Toplam Kazanım</p>
            <p className="text-3xl font-bold text-gray-900">{totalStats.totalOutcomes}</p>
          </div>
          {groupedData.map(status => (
            <div key={status.status} className={`rounded-lg shadow p-6 border-2 ${getStatusColor(status.status)}`}>
              <p className="text-sm text-gray-600 mb-1">{getStatusIcon(status.status)} {status.label}</p>
              <p className="text-3xl font-bold text-gray-900">{status.stats.totalOutcomes}</p>
            </div>
          ))}
        </div>

        {/* Hierarchical Groups */}
        <div className="space-y-4">
          {groupedData.map(statusGroup => {
            if (statusGroup.stats.totalOutcomes === 0) return null;

            const statusId = `status-${statusGroup.status}`;
            const isStatusExpanded = expandedGroups.has(statusId);

            return (
              <div key={statusGroup.status} className={`bg-white rounded-lg shadow border-l-4 ${getStatusColor(statusGroup.status).replace('bg-', 'border-').replace('-50', '-500')}`}>
                {/* Status Header */}
                <button
                  onClick={() => toggleGroup(statusId)}
                  className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <span className="text-2xl">{getStatusIcon(statusGroup.status)}</span>
                    <div className="text-left">
                      <h2 className="text-xl font-bold text-gray-900">{statusGroup.label}</h2>
                      <div className="flex gap-6 mt-2 text-sm text-gray-600">
                        <span>Kayıt Sayısı: <strong>{statusGroup.stats.totalOutcomes}</strong></span>
                        <span>Görülme: <strong>{statusGroup.stats.totalAppearances}</strong></span>
                        <span>Soru: <strong>{statusGroup.stats.totalQuestions}</strong></span>
                        <span>Kazanılan: <strong>{statusGroup.stats.totalAcquired}</strong></span>
                        <span>Oran: <strong>{statusGroup.stats.averageSuccessRate.toFixed(1)}%</strong></span>
                      </div>
                    </div>
                  </div>
                  <svg
                    className={`w-6 h-6 transition-transform ${isStatusExpanded ? 'transform rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Subjects */}
                {isStatusExpanded && (
                  <div className="px-6 pb-6 space-y-3">
                    {statusGroup.subjects.map(subjectGroup => {
                      const subjectId = `subject-${statusGroup.status}-${subjectGroup.subject}`;
                      const isSubjectExpanded = expandedGroups.has(subjectId);

                      return (
                        <div key={subjectGroup.subject} className="bg-gray-50 rounded-lg border border-gray-200">
                          {/* Subject Header */}
                          <button
                            onClick={() => toggleGroup(subjectId)}
                            className="w-full p-4 flex items-center justify-between hover:bg-gray-100 transition-colors rounded-lg"
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-xl">📚</span>
                              <div className="text-left">
                                <h3 className="font-semibold text-gray-900">{subjectGroup.subject}</h3>
                                <div className="flex gap-4 mt-1 text-xs text-gray-600">
                                  <span>Kayıt Sayısı: <strong>{subjectGroup.stats.totalOutcomes}</strong></span>
                                  <span>Görülme: <strong>{subjectGroup.stats.totalAppearances}</strong></span>
                                  <span>Soru: <strong>{subjectGroup.stats.totalQuestions}</strong></span>
                                  <span>Kazanılan: <strong>{subjectGroup.stats.totalAcquired}</strong></span>
                                  <span>Oran: <strong>{subjectGroup.stats.averageSuccessRate.toFixed(1)}%</strong></span>
                                </div>
                              </div>
                            </div>
                            <svg
                              className={`w-5 h-5 transition-transform ${isSubjectExpanded ? 'transform rotate-180' : ''}`}
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </button>

                          {/* Categories */}
                          {isSubjectExpanded && (
                            <div className="px-4 pb-4 space-y-2">
                              {subjectGroup.categories.map(categoryGroup => {
                                const categoryId = `category-${statusGroup.status}-${subjectGroup.subject}-${categoryGroup.category}`;
                                const isCategoryExpanded = expandedGroups.has(categoryId);

                                return (
                                  <div key={categoryGroup.category} className="bg-white rounded-lg border border-gray-200">
                                    {/* Category Header */}
                                    <button
                                      onClick={() => toggleGroup(categoryId)}
                                      className="w-full p-3 flex items-center justify-between hover:bg-gray-50 transition-colors rounded-lg"
                                    >
                                      <div className="flex items-center gap-2">
                                        <span className="text-lg">📁</span>
                                        <div className="text-left">
                                          <h4 className="font-medium text-gray-900 text-sm">{categoryGroup.category}</h4>
                                          <div className="flex gap-3 mt-1 text-xs text-gray-500">
                                            <span>Kayıt Sayısı: <strong>{categoryGroup.stats.totalOutcomes}</strong></span>
                                            <span>Soru: <strong>{categoryGroup.stats.totalQuestions}</strong></span>
                                            <span>Kazanılan: <strong>{categoryGroup.stats.totalAcquired}</strong></span>
                                            <span>Oran: <strong>{categoryGroup.stats.averageSuccessRate.toFixed(1)}%</strong></span>
                                          </div>
                                        </div>
                                      </div>
                                      <svg
                                        className={`w-4 h-4 transition-transform ${isCategoryExpanded ? 'transform rotate-180' : ''}`}
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                      >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                      </svg>
                                    </button>

                                    {/* Subcategories */}
                                    {isCategoryExpanded && (
                                      <div className="px-3 pb-3 space-y-2">
                                        {categoryGroup.subcategories.map(subcategoryGroup => {
                                          const subcategoryId = `subcategory-${statusGroup.status}-${subjectGroup.subject}-${categoryGroup.category}-${subcategoryGroup.subcategory}`;
                                          const isSubcategoryExpanded = expandedGroups.has(subcategoryId);

                                          return (
                                            <div key={subcategoryGroup.subcategory} className="bg-gray-50 rounded border border-gray-200">
                                              {/* Subcategory Header */}
                                              <button
                                                onClick={() => toggleGroup(subcategoryId)}
                                                className="w-full p-2 flex items-center justify-between hover:bg-gray-100 transition-colors rounded"
                                              >
                                                <div className="flex items-center gap-2">
                                                  <span className="text-sm">📋</span>
                                                  <div className="text-left">
                                                    <h5 className="font-medium text-gray-900 text-xs">{subcategoryGroup.subcategory}</h5>
                                                    <div className="flex gap-2 mt-0.5 text-xs text-gray-500">
                                                      <span>Kayıt Sayısı: <strong>{subcategoryGroup.stats.totalOutcomes}</strong></span>
                                                      <span>Soru: <strong>{subcategoryGroup.stats.totalQuestions}</strong></span>
                                                      <span>Oran: <strong>{subcategoryGroup.stats.averageSuccessRate.toFixed(1)}%</strong></span>
                                                    </div>
                                                  </div>
                                                </div>
                                                <svg
                                                  className={`w-4 h-4 transition-transform ${isSubcategoryExpanded ? 'transform rotate-180' : ''}`}
                                                  fill="none"
                                                  stroke="currentColor"
                                                  viewBox="0 0 24 24"
                                                >
                                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                </svg>
                                              </button>

                                              {/* Outcomes List */}
                                              {isSubcategoryExpanded && (
                                                <div className="px-2 pb-2">
                                                  <div className="bg-white rounded border border-gray-200 overflow-hidden">
                                                    <table className="w-full text-xs">
                                                      <thead className="bg-gray-100">
                                                        <tr>
                                                          <th className="px-2 py-1 text-left">Kazanım</th>
                                                          <th className="px-2 py-1 text-center">Görülme</th>
                                                          <th className="px-2 py-1 text-center">Soru</th>
                                                          <th className="px-2 py-1 text-center">Kazanılan</th>
                                                          <th className="px-2 py-1 text-center">Başarı Oranı</th>
                                                        </tr>
                                                      </thead>
                                                      <tbody>
                                                        {subcategoryGroup.outcomes.map((outcome, idx) => (
                                                          <tr key={idx} className="border-t hover:bg-gray-50">
                                                            <td className="px-2 py-2 max-w-xs truncate">
                                                              {outcome.outcome_description || '-'}
                                                            </td>
                                                            <td className="px-2 py-2 text-center">{outcome.total_appearances}</td>
                                                            <td className="px-2 py-2 text-center">{outcome.total_questions}</td>
                                                            <td className="px-2 py-2 text-center">{outcome.total_acquired}</td>
                                                            <td className="px-2 py-2 text-center">
                                                              <div className="flex flex-col items-center gap-1">
                                                                <span className="font-medium">{outcome.average_success_rate.toFixed(1)}%</span>
                                                                <div className="w-full bg-gray-200 rounded-full h-1.5">
                                                                  <div
                                                                    className={`h-1.5 rounded-full ${getSuccessRateColor(outcome.average_success_rate)}`}
                                                                    style={{ width: `${outcome.average_success_rate}%` }}
                                                                  ></div>
                                                                </div>
                                                              </div>
                                                            </td>
                                                          </tr>
                                                        ))}
                                                      </tbody>
                                                    </table>
                                                  </div>
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
                )}
              </div>
            );
          })}
        </div>

        {/* Help Text */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>İpucu:</strong> Her seviyeyi tıklayarak detaylara inebilirsiniz.
            Kazanımlar başarı durumuna göre gruplandırılmıştır.
            Zayıf görünen kazanımlar üzerinde daha fazla çalışma yapılması önerilir.
          </p>
        </div>
      </div>
    </div>
  );
};
