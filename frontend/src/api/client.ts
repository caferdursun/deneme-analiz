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
