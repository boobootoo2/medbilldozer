/**
 * Main App component with routing
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { InviteCodeGate } from './components/auth/InviteCodeGate';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { HomePage } from './pages/HomePage';
import { AnalysisDashboard } from './components/analysis/AnalysisDashboard';
import { DisclaimerModal } from './components/DisclaimerModal';

function App() {
  return (
    <BrowserRouter>
      <DisclaimerModal />
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

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
