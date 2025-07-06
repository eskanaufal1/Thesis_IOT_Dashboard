import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import DevicePage from "./pages/DevicePage";
import StatisticPage from "./pages/StatisticPage";
import ChatbotPage from "./pages/ChatbotPage";
import ProfilePage from "./pages/ProfilePage";

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public route - Login page */}
            <Route path="/" element={<LoginPage />} />
            
            {/* Protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/device" element={
              <ProtectedRoute>
                <Layout>
                  <DevicePage />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/statistic" element={
              <ProtectedRoute>
                <Layout>
                  <StatisticPage />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/chatbot" element={
              <ProtectedRoute>
                <Layout>
                  <ChatbotPage />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Layout>
                  <ProfilePage />
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
    </ThemeProvider>
  );
};

export default App;
