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
