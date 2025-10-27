import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from './components/ErrorBoundary';

// Eager load critical pages for faster initial render
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';

// Lazy load less critical pages for better performance
const ExamListPage = lazy(() => import('./pages/ExamListPage').then(m => ({ default: m.ExamListPage })));
const ExamDetailPage = lazy(() => import('./pages/ExamDetailPage').then(m => ({ default: m.ExamDetailPage })));
const SubjectAnalysisPage = lazy(() => import('./pages/SubjectAnalysisPage').then(m => ({ default: m.SubjectAnalysisPage })));
const RecommendationsPage = lazy(() => import('./pages/RecommendationsPage').then(m => ({ default: m.RecommendationsPage })));
const ValidationReviewPage = lazy(() => import('./pages/ValidationReviewPage').then(m => ({ default: m.ValidationReviewPage })));
const CleanupWizardPage = lazy(() => import('./pages/CleanupWizardPage').then(m => ({ default: m.CleanupWizardPage })));
const StudyPlanWizardPage = lazy(() => import('./pages/StudyPlanWizardPage'));
const StudyPlanPage = lazy(() => import('./pages/StudyPlanPage'));
const StudyPlanListPage = lazy(() => import('./pages/StudyPlanListPage'));
const TopicTreePage = lazy(() => import('./pages/TopicTreePage'));

// Loading component
const PageLoader = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p className="mt-4 text-gray-600">Yükleniyor...</p>
    </div>
  </div>
);

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
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/exams" element={<ExamListPage />} />
          <Route path="/exams/:examId" element={<ExamDetailPage />} />
          <Route path="/exams/:examId/validate" element={<ValidationReviewPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/subjects/:subjectName" element={<SubjectAnalysisPage />} />
          <Route path="/learning-outcomes/cleanup" element={<CleanupWizardPage />} />
          <Route path="/learning-outcomes/tree" element={<TopicTreePage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/study-plans" element={<StudyPlanListPage />} />
          <Route path="/study-plan/create" element={<StudyPlanWizardPage />} />
          <Route path="/study-plan/:planId" element={<StudyPlanPage />} />
        </Routes>
      </Suspense>
    </Router>
    </ErrorBoundary>
  );
}

export default App;
