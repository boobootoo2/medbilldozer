/**
 * Main App component with routing
 */
import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { InviteCodeGate } from './components/auth/InviteCodeGate';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { HomePage } from './pages/HomePage';
import { AnalysisDashboard } from './components/analysis/AnalysisDashboard';
import DocumentManagementPage from './pages/DocumentManagementPage';
import { DisclaimerModal } from './components/DisclaimerModal';
import { CookieConsentDialog } from './components/CookieConsentDialog';
import { initGA, trackPageView } from './utils/analytics';

/**
 * Analytics tracker component
 * Tracks page views on route changes
 */
function AnalyticsTracker() {
  const location = useLocation();

  useEffect(() => {
    // Track page view whenever location changes
    trackPageView(location.pathname);
  }, [location]);

  return null;
}

function App() {
  useEffect(() => {
    // Initialize Google Analytics 4 on app mount
    initGA();
  }, []);

  return (
    <BrowserRouter>
      <AnalyticsTracker />
      <DisclaimerModal />
      <CookieConsentDialog />
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<InviteCodeGate />} />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis/:analysisId"
          element={
            <ProtectedRoute>
              <AnalysisDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents"
          element={
            <ProtectedRoute>
              <DocumentManagementPage />
            </ProtectedRoute>
          }
        />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
