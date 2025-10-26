import axios from 'axios';
import type {
  ExamListResponse,
  ExamDetail,
  ExamUploadResponse,
  AnalyticsOverview,
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
};
