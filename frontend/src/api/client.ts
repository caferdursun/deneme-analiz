import axios from 'axios';
import type {
  ExamListResponse,
  ExamDetail,
  ExamUploadResponse,
  ExamConfirmResponse,
  AnalyticsOverview,
  SubjectAnalytics,
  LearningOutcomeStats,
  RecommendationsListResponse,
  RecommendationRefreshResponse,
  StudyPlan,
  StudyPlanGenerateRequest,
  StudyPlanListResponse,
  StudyPlanProgress,
  Resource,
  ResourceListResponse,
  CuratedResourcesResponse,
} from '../types';

// Use relative URL to work with Vite proxy
const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const examAPI = {
  // Upload exam PDF
  uploadExam: async (file: File): Promise<ExamUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ExamUploadResponse>(
      '/exams/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Get all exams
  getExams: async (studentId?: string): Promise<ExamListResponse> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<ExamListResponse>('/exams', { params });
    return response.data;
  },

  // Get exam details
  getExamDetail: async (examId: string): Promise<ExamDetail> => {
    const response = await apiClient.get<ExamDetail>(`/exams/${examId}`);
    return response.data;
  },

  // Delete exam
  deleteExam: async (examId: string): Promise<void> => {
    await apiClient.delete(`/exams/${examId}`);
  },

  // Confirm exam with chosen data source
  confirmExam: async (examId: string, dataSource: 'claude' | 'local'): Promise<ExamConfirmResponse> => {
    const response = await apiClient.post<ExamConfirmResponse>(
      `/exams/${examId}/confirm`,
      { data_source: dataSource }
    );
    return response.data;
  },

  // Get pending exams count
  getPendingCount: async (studentId?: string): Promise<{ pending_count: number; student_id?: string }> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<{ pending_count: number; student_id?: string }>('/exams/stats/pending-count', { params });
    return response.data;
  },
};

export const analyticsAPI = {
  // Get analytics overview
  getOverview: async (studentId?: string): Promise<AnalyticsOverview> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<AnalyticsOverview>('/analytics/overview', { params });
    return response.data;
  },

  // Get subject analytics
  getSubjectAnalytics: async (subjectName: string, studentId?: string): Promise<SubjectAnalytics> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<SubjectAnalytics>(`/analytics/subjects/${encodeURIComponent(subjectName)}`, { params });
    return response.data;
  },

  // Get all learning outcomes
  getAllLearningOutcomes: async (studentId?: string): Promise<LearningOutcomeStats[]> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<LearningOutcomeStats[]>('/analytics/learning-outcomes', { params });
    return response.data;
  },

  // Get learning outcomes tree
  getLearningOutcomesTree: async (studentId?: string): Promise<{ tree: any[] }> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<{ tree: any[] }>('/analytics/learning-outcomes/tree', { params });
    return response.data;
  },
};

export const recommendationsAPI = {
  // Get active recommendations
  getRecommendations: async (studentId?: string): Promise<RecommendationsListResponse> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<RecommendationsListResponse>('/recommendations', { params });
    return response.data;
  },

  // Refresh recommendations
  refreshRecommendations: async (studentId?: string): Promise<RecommendationRefreshResponse> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.post<RecommendationRefreshResponse>('/recommendations/refresh', null, { params });
    return response.data;
  },

  // Mark recommendation as complete
  markAsComplete: async (recommendationId: string): Promise<{ message: string; id: string }> => {
    const response = await apiClient.post<{ message: string; id: string }>(`/recommendations/${recommendationId}/complete`);
    return response.data;
  },
};

export const learningOutcomesAPI = {
  // Analyze learning outcomes for similarity
  analyzeOutcomes: async (studentId?: string): Promise<any> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get('/learning-outcomes/analyze', { params });
    return response.data;
  },

  // Perform cleanup with approved merge groups
  cleanupOutcomes: async (mergeGroups: any[], mergedBy: string = 'user'): Promise<any> => {
    const response = await apiClient.post('/learning-outcomes/cleanup', {
      merge_groups: mergeGroups,
      merged_by: mergedBy
    });
    return response.data;
  },

  // Undo a merge operation
  undoMerge: async (mergeGroupId: string, undoneBy: string = 'user'): Promise<any> => {
    const response = await apiClient.post(`/learning-outcomes/undo/${mergeGroupId}`, { undone_by: undoneBy });
    return response.data;
  },

  // Get merge history
  getMergeHistory: async (limit: number = 50, includeUndone: boolean = false): Promise<any> => {
    const response = await apiClient.get('/learning-outcomes/merge-history', {
      params: { limit, include_undone: includeUndone }
    });
    return response.data;
  },
};

export const studyPlansAPI = {
  // Generate a new study plan
  generate: async (request: StudyPlanGenerateRequest): Promise<StudyPlan> => {
    const response = await apiClient.post<StudyPlan>('/study-plans/generate', request);
    return response.data;
  },

  // Get study plan by ID
  getById: async (planId: string): Promise<StudyPlan> => {
    const response = await apiClient.get<StudyPlan>(`/study-plans/${planId}`);
    return response.data;
  },

  // Get active study plan
  getActive: async (studentId?: string): Promise<StudyPlan> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<StudyPlan>('/study-plans/active/current', { params });
    return response.data;
  },

  // List all study plans
  list: async (studentId?: string): Promise<StudyPlanListResponse> => {
    const params = studentId ? { student_id: studentId } : {};
    const response = await apiClient.get<StudyPlanListResponse>('/study-plans', { params });
    return response.data;
  },

  // Update item completion status
  updateItemCompletion: async (planId: string, itemId: string, completed: boolean): Promise<{ success: boolean; item_id: string; completed: boolean }> => {
    const response = await apiClient.put<{ success: boolean; item_id: string; completed: boolean }>(
      `/study-plans/${planId}/items/${itemId}/complete`,
      { completed }
    );
    return response.data;
  },

  // Get progress for a study plan
  getProgress: async (planId: string): Promise<StudyPlanProgress> => {
    const response = await apiClient.get<StudyPlanProgress>(`/study-plans/${planId}/progress`);
    return response.data;
  },

  // Archive a study plan
  archive: async (planId: string): Promise<{ success: boolean; plan_id: string; status: string }> => {
    const response = await apiClient.put<{ success: boolean; plan_id: string; status: string }>(`/study-plans/${planId}/archive`);
    return response.data;
  },

  // Delete a study plan
  delete: async (planId: string): Promise<void> => {
    await apiClient.delete(`/study-plans/${planId}`);
  },
};

// Resource API
export const resourceAPI = {
  // Get all resources
  getAll: async (subject?: string): Promise<Resource[]> => {
    const params = subject ? { subject } : {};
    const response = await apiClient.get<ResourceListResponse>('/resources', { params });
    return response.data.resources;
  },

  // Get resources for a recommendation
  getRecommendationResources: async (recId: string): Promise<Resource[]> => {
    const response = await apiClient.get<Resource[]>(`/resources/recommendations/${recId}`);
    return response.data;
  },

  // Auto-link resources to a recommendation
  autoLinkResources: async (recId: string, subject: string, topic: string, count: number = 3): Promise<Resource[]> => {
    const response = await apiClient.post<Resource[]>(
      `/resources/recommendations/${recId}/auto-link`,
      null,
      { params: { subject, topic, count } }
    );
    return response.data;
  },

  // Use Claude AI to curate resources for a recommendation
  curateResources: async (recId: string): Promise<CuratedResourcesResponse> => {
    const response = await apiClient.post<CuratedResourcesResponse>(
      `/resources/recommendations/${recId}/curate`
    );
    return response.data;
  },

  // Delete a resource with optional blacklisting
  deleteResource: async (resourceId: string, blacklist: boolean = true, reason?: string): Promise<{ message: string; resource_id: string; blacklisted: boolean }> => {
    const params: any = { blacklist };
    if (reason) {
      params.reason = reason;
    }
    const response = await apiClient.delete<{ message: string; resource_id: string; blacklisted: boolean }>(
      `/resources/${resourceId}`,
      { params }
    );
    return response.data;
  },
};
