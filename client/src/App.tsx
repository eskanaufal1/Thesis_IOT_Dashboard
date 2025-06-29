import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import Layout from "./components/Layout";
import DashboardPage from "./pages/DashboardPage";
import DevicePage from "./pages/DevicePage";
import StatisticPage from "./pages/StatisticPage";
import ChatbotPage from "./pages/ChatbotPage";

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/device" element={<DevicePage />} />
            <Route path="/statistic" element={<StatisticPage />} />
            <Route path="/chatbot" element={<ChatbotPage />} />
            <Route path="*" element={
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
            } />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
};

export default App;
