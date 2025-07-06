import React, { Suspense } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import { ToastProvider } from "./contexts/ToastContext";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import ErrorBoundary from "./components/ErrorBoundary";
import LoginPage from "./pages/LoginPage";

// Lazy load pages for better performance
const DashboardPage = React.lazy(() => import("./pages/DashboardPage"));
const DevicePage = React.lazy(() => import("./pages/DevicePage"));
const StatisticPage = React.lazy(() => import("./pages/StatisticPage"));
const ChatbotPage = React.lazy(() => import("./pages/ChatbotPage"));
const ProfilePage = React.lazy(() => import("./pages/ProfilePage"));

// Loading component
const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center h-64 space-y-4">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    <p className="text-gray-600 dark:text-gray-400 text-sm">Loading...</p>
  </div>
);

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <Router>
              <Routes>
                {/* Public route - Login page */}
            <Route path="/" element={<LoginPage />} />
            
            {/* Protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Suspense fallback={<LoadingSpinner />}>
                    <DashboardPage />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/device" element={
              <ProtectedRoute>
                <Layout>
                  <Suspense fallback={<LoadingSpinner />}>
                    <DevicePage />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/statistic" element={
              <ProtectedRoute>
                <Layout>
                  <Suspense fallback={<LoadingSpinner />}>
                    <StatisticPage />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/chatbot" element={
              <ProtectedRoute>
                <Layout>
                  <Suspense fallback={<LoadingSpinner />}>
                    <ChatbotPage />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Layout>
                  <Suspense fallback={<LoadingSpinner />}>
                    <ProfilePage />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            } />
            
            {/* 404 page */}
            <Route path="*" element={
              <ProtectedRoute>
                <Layout>
                  <div className="flex items-center justify-center h-64">
                    <div className="text-center">
                      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                        404 - Page Not Found
                      </h1>
                      <p className="text-gray-600 dark:text-gray-400">
                        The page you're looking for doesn't exist.
                      </p>
                    </div>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ToastProvider>
  </ThemeProvider>
</ErrorBoundary>
  );
};

export default App;
