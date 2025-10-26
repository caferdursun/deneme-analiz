import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';
import { ExamListPage } from './pages/ExamListPage';
import { ExamDetailPage } from './pages/ExamDetailPage';
import { SubjectAnalysisPage } from './pages/SubjectAnalysisPage';
import { LearningOutcomesPage } from './pages/LearningOutcomesPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { ValidationReviewPage } from './pages/ValidationReviewPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/exams" element={<ExamListPage />} />
        <Route path="/exams/:examId" element={<ExamDetailPage />} />
        <Route path="/exams/:examId/validate" element={<ValidationReviewPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/subjects/:subjectName" element={<SubjectAnalysisPage />} />
        <Route path="/learning-outcomes" element={<LearningOutcomesPage />} />
        <Route path="/recommendations" element={<RecommendationsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
