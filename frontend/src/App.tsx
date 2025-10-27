import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';
import { ExamListPage } from './pages/ExamListPage';
import { ExamDetailPage } from './pages/ExamDetailPage';
import { SubjectAnalysisPage } from './pages/SubjectAnalysisPage';
import { LearningOutcomesPage } from './pages/LearningOutcomesPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { ValidationReviewPage } from './pages/ValidationReviewPage';
import { CleanupWizardPage } from './pages/CleanupWizardPage';
import StudyPlanWizardPage from './pages/StudyPlanWizardPage';
import StudyPlanPage from './pages/StudyPlanPage';

function App() {
  return (
    <ErrorBoundary>
      <Router>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#363636',
            padding: '16px',
            borderRadius: '8px',
            fontSize: '14px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/exams" element={<ExamListPage />} />
        <Route path="/exams/:examId" element={<ExamDetailPage />} />
        <Route path="/exams/:examId/validate" element={<ValidationReviewPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/subjects/:subjectName" element={<SubjectAnalysisPage />} />
        <Route path="/learning-outcomes" element={<LearningOutcomesPage />} />
        <Route path="/learning-outcomes/cleanup" element={<CleanupWizardPage />} />
        <Route path="/recommendations" element={<RecommendationsPage />} />
        <Route path="/study-plan/create" element={<StudyPlanWizardPage />} />
        <Route path="/study-plan/:planId" element={<StudyPlanPage />} />
      </Routes>
    </Router>
    </ErrorBoundary>
  );
}

export default App;
