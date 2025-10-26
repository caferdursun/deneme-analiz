export interface Student {
  id: string;
  name: string;
  school: string | null;
  grade: string | null;
  class_section: string | null;
  created_at: string;
}

export interface Exam {
  id: string;
  student_id: string;
  exam_name: string;
  exam_date: string;
  booklet_type: string | null;
  pdf_path: string | null;
  uploaded_at: string;
  processed_at: string | null;
  created_at: string;
  status?: string;
  claude_data?: string;
  local_data?: string;
  validation_report?: string;
  confirmed_at?: string | null;
}

export interface ExamResult {
  total_questions: number;
  total_correct: number;
  total_wrong: number;
  total_blank: number;
  net_score: number;
  net_percentage: number;
  class_rank: number | null;
  class_total: number | null;
  school_rank: number | null;
  school_total: number | null;
  class_avg: number | null;
  school_avg: number | null;
}

export interface SubjectResult {
  id: string;
  subject_name: string;
  total_questions: number;
  correct: number;
  wrong: number;
  blank: number;
  net_score: number;
  net_percentage: number;
  class_rank: number | null;
  class_avg: number | null;
  school_rank: number | null;
  school_avg: number | null;
}

export interface LearningOutcome {
  id: string;
  subject_name: string;
  category: string | null;
  subcategory: string | null;
  outcome_description: string | null;
  total_questions: number;
  acquired: number;
  lost: number;
  success_rate: number | null;
  student_percentage: number | null;
  class_percentage: number | null;
  school_percentage: number | null;
}

export interface Question {
  id: string;
  subject_name: string;
  question_number: number;
  correct_answer: string | null;
  student_answer: string | null;
  is_correct: boolean;
  is_blank: boolean;
  is_canceled: boolean;
}

export interface ExamDetail {
  exam: Exam;
  student: Student;
  overall_result: ExamResult | null;
  subject_results: SubjectResult[];
  learning_outcomes: LearningOutcome[];
  questions: Question[];
}

export interface ExamListResponse {
  exams: Exam[];
  total: number;
}

export interface ValidationIssue {
  field: string;
  claude_value: any;
  local_value: any;
  severity: string;
}

export interface ValidationReport {
  status: string;
  total_issues: number;
  errors: number;
  warnings: number;
  info: number;
  issues: ValidationIssue[];
  summary: string;
}

export interface ExamUploadResponse {
  exam_id: string;
  message: string;
  status: string;
  validation_report: ValidationReport | null;
}

export interface ExamConfirmResponse {
  message: string;
  exam_id: string;
  data_source: string;
  status: string;
}

// Analytics types
export interface OverviewStats {
  total_exams: number;
  latest_net_score: number | null;
  average_net_score: number | null;
  best_score: number | null;
  worst_score: number | null;
  total_questions_answered: number;
  overall_accuracy: number | null;
}

export interface ScoreTrend {
  exam_id: string;
  exam_name: string;
  exam_date: string;
  net_score: number;
  net_percentage: number;
  class_rank: number | null;
  school_rank: number | null;
}

export interface SubjectPerformance {
  subject_name: string;
  total_exams: number;
  average_net: number;
  average_percentage: number;
  best_net: number;
  worst_net: number;
  total_questions: number;
  total_correct: number;
  total_wrong: number;
  total_blank: number;
  improvement_trend: string | null;
}

export interface AnalyticsOverview {
  stats: OverviewStats;
  score_trends: ScoreTrend[];
  top_subjects: SubjectPerformance[];
  weak_subjects: SubjectPerformance[];
}

export interface SubjectTrend {
  exam_id: string;
  exam_name: string;
  exam_date: string;
  subject_name: string;
  net_score: number;
  net_percentage: number;
  correct: number;
  wrong: number;
  blank: number;
}

export interface LearningOutcomeStats {
  subject_name: string;
  category: string | null;
  subcategory: string | null;
  outcome_description: string | null;
  total_appearances: number;
  total_questions: number;
  total_acquired: number;
  average_success_rate: number;
  improvement_trend: string | null;
}

export interface SubjectAnalytics {
  subject_name: string;
  performance: SubjectPerformance;
  trends: SubjectTrend[];
  learning_outcomes: LearningOutcomeStats[];
}

// Recommendation types
export interface Recommendation {
  id: string;
  student_id: string;
  priority: number;
  subject_name: string | null;
  topic: string | null;
  issue_type: string;
  description: string;
  action_items: string[];
  rationale: string | null;
  impact_score: number | null;
  is_active: boolean;
  generated_at: string;
  created_at: string;

  // New tracking fields
  learning_outcome_ids: string[] | null;  // Links to specific learning outcomes
  status: string;  // 'new', 'active', 'updated', 'resolved', 'superseded'
  last_confirmed_at: string | null;  // When this recommendation was last confirmed
  previous_recommendation_id: string | null;  // Link to previous version
}

export interface RefreshSummary {
  new_count: number;  // Brand new recommendations
  updated_count: number;  // Updated versions of existing recommendations
  confirmed_count: number;  // Existing recommendations still valid
  resolved_count: number;  // Issues that are no longer present
  total_active: number;  // Total active recommendations after refresh
}

export interface RecommendationsListResponse {
  recommendations: Recommendation[];
  total: number;
}

export interface RecommendationRefreshResponse {
  message: string;
  count: number;
  recommendations: Recommendation[];
  summary: RefreshSummary;  // Detailed change summary
}
