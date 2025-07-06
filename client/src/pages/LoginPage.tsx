import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth, validatePassword } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';

const LoginPage: React.FC = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const { login, register } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (isSignUp) {
      if (!formData.name.trim()) newErrors.name = 'Name is required';
      if (!formData.email.trim()) newErrors.email = 'Email is required';
      if (!formData.email.includes('@')) newErrors.email = 'Please enter a valid email';
      if (!formData.username.trim()) newErrors.username = 'Username is required';
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    } else {
      if (!formData.username.trim()) newErrors.username = 'Username is required';
    }

    if (!formData.password.trim()) newErrors.password = 'Password is required';

    if (formData.password && !validatePassword(formData.password).isValid) {
      newErrors.password = 'Password does not meet requirements';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    
    try {
      if (isSignUp) {
        const success = await register(formData.username, formData.email, formData.password, formData.name);
        if (success) {
          // Switch to login mode after successful registration
          setIsSignUp(false);
          setFormData({
            name: '',
            email: '',
            username: formData.username, // Keep the username for easier login
            password: '',
            confirmPassword: ''
          });
          setErrors({});
        }
      } else {
        const success = await login(formData.username, formData.password);
        if (success) {
          navigate('/dashboard');
        } else {
          setErrors({ username: 'Invalid username or password' });
        }
      }
    } catch {
      setErrors({ general: 'An error occurred. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const passwordValidation = validatePassword(formData.password);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Dark Mode Toggle Button */}
      <motion.button
        onClick={toggleTheme}
        className="fixed top-6 right-6 z-50 p-3 rounded-full bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:scale-105 transition-all duration-200"
        aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <span className="text-xl">
          {theme === 'light' ? '🌙' : '☀️'}
        </span>
      </motion.button>

      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-80 h-80 bg-blue-200 dark:bg-blue-900 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-xl opacity-30 animate-blob"></div>
        <div className="absolute -bottom-40 -right-40 w-80 h-80 bg-blue-300 dark:bg-blue-800 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 right-40 w-60 h-60 bg-blue-100 dark:bg-blue-700 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
        
        {/* Geometric shapes similar to the reference */}
        <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-700 dark:to-blue-800 transform skew-y-2 origin-bottom-left opacity-10"></div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-400 dark:bg-blue-600 opacity-5 dark:opacity-20 transform rotate-45 -translate-y-32 translate-x-32"></div>
      </div>

      <motion.div 
        className="relative z-10 w-full max-w-6xl bg-white dark:bg-gray-800 rounded-3xl shadow-2xl overflow-hidden"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex flex-col lg:flex-row min-h-[600px]">
          {/* Left Side - Illustration */}
          <motion.div 
            className="lg:w-1/2 bg-gradient-to-br from-blue-50 via-white to-blue-100 dark:from-gray-700 dark:to-gray-800 p-8 lg:p-12 flex items-center justify-center relative overflow-hidden"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-blue-50 dark:bg-gray-700 opacity-50">
              <div className="absolute inset-0" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%235B9BD5' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              }}></div>
            </div>

            {/* Decorative elements */}
            <div className="absolute top-10 left-10 w-16 h-16 bg-blue-200 dark:bg-blue-400 rounded-full opacity-20 animate-pulse"></div>
            <div className="absolute bottom-10 right-10 w-12 h-12 bg-blue-300 dark:bg-blue-300 rounded-full opacity-30 animate-bounce"></div>
            <div className="absolute top-20 right-20 w-8 h-8 bg-cyan-300 dark:bg-cyan-400 rounded-full opacity-40 animate-pulse"></div>

            <div className="relative z-10 text-center max-w-md">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                {/* Modern Security Illustration */}
                <div className="mb-8">
                  <svg className="w-80 h-80 mx-auto" viewBox="0 0 400 400" fill="none" xmlns="http://www.w3.org/2000/svg">
                    {/* Background circle */}
                    <circle cx="200" cy="200" r="180" fill="rgba(59, 130, 246, 0.05)" />
                    
                    {/* Main computer/monitor */}
                    <rect x="150" y="120" width="100" height="80" rx="8" fill="#1E40AF" />
                    <rect x="155" y="125" width="90" height="55" rx="4" fill="#3B82F6" />
                    <rect x="160" y="130" width="80" height="6" rx="3" fill="rgba(255,255,255,0.9)" />
                    <rect x="160" y="140" width="60" height="6" rx="3" fill="rgba(255,255,255,0.7)" />
                    <rect x="160" y="150" width="40" height="4" rx="2" fill="rgba(255,255,255,0.5)" />
                    
                    {/* Monitor stand */}
                    <rect x="195" y="200" width="10" height="20" rx="2" fill="#1E40AF" />
                    <rect x="180" y="220" width="40" height="8" rx="4" fill="#1E40AF" />
                    
                    {/* Central shield */}
                    <path d="M200 160 L200 240 L220 250 L240 240 L240 160 L220 150 Z" fill="#10B981" />
                    <path d="M210 170 L210 225 L220 235 L230 225 L230 170 L220 165 Z" fill="#059669" />
                    <circle cx="220" cy="190" r="12" fill="white" />
                    <rect x="216" y="186" width="8" height="8" rx="2" fill="#059669" />
                    
                    {/* Lock icons around */}
                    <g transform="translate(100, 100)">
                      <rect x="0" y="8" width="20" height="16" rx="2" fill="#6366F1" />
                      <rect x="4" y="12" width="12" height="8" rx="1" fill="white" />
                      <path d="M10 6 C10 3, 12 1, 15 1 C18 1, 20 3, 20 6 L20 8 L0 8 L0 6 C0 3, 2 1, 5 1 C8 1, 10 3, 10 6" stroke="#6366F1" strokeWidth="2" fill="none" />
                    </g>
                    
                    <g transform="translate(280, 100)">
                      <rect x="0" y="8" width="20" height="16" rx="2" fill="#06B6D4" />
                      <rect x="4" y="12" width="12" height="8" rx="1" fill="white" />
                      <path d="M10 6 C10 3, 12 1, 15 1 C18 1, 20 3, 20 6 L20 8 L0 8 L0 6 C0 3, 2 1, 5 1 C8 1, 10 3, 10 6" stroke="#06B6D4" strokeWidth="2" fill="none" />
                    </g>
                    
                    <g transform="translate(100, 280)">
                      <rect x="0" y="8" width="20" height="16" rx="2" fill="#8B5CF6" />
                      <rect x="4" y="12" width="12" height="8" rx="1" fill="white" />
                      <path d="M10 6 C10 3, 12 1, 15 1 C18 1, 20 3, 20 6 L20 8 L0 8 L0 6 C0 3, 2 1, 5 1 C8 1, 10 3, 10 6" stroke="#8B5CF6" strokeWidth="2" fill="none" />
                    </g>
                    
                    <g transform="translate(280, 280)">
                      <rect x="0" y="8" width="20" height="16" rx="2" fill="#F59E0B" />
                      <rect x="4" y="12" width="12" height="8" rx="1" fill="white" />
                      <path d="M10 6 C10 3, 12 1, 15 1 C18 1, 20 3, 20 6 L20 8 L0 8 L0 6 C0 3, 2 1, 5 1 C8 1, 10 3, 10 6" stroke="#F59E0B" strokeWidth="2" fill="none" />
                    </g>
                    
                    {/* Globe/Network */}
                    <circle cx="120" cy="200" r="25" fill="rgba(59, 130, 246, 0.1)" stroke="#3B82F6" strokeWidth="2" />
                    <path d="M95 200 Q120 180 145 200 Q120 220 95 200" fill="none" stroke="#3B82F6" strokeWidth="1.5" />
                    <path d="M95 200 Q120 220 145 200 Q120 180 95 200" fill="none" stroke="#3B82F6" strokeWidth="1.5" />
                    <line x1="95" y1="200" x2="145" y2="200" stroke="#3B82F6" strokeWidth="1.5" />
                    
                    {/* Globe/Network 2 */}
                    <circle cx="280" cy="200" r="25" fill="rgba(6, 182, 212, 0.1)" stroke="#06B6D4" strokeWidth="2" />
                    <path d="M255 200 Q280 180 305 200 Q280 220 255 200" fill="none" stroke="#06B6D4" strokeWidth="1.5" />
                    <path d="M255 200 Q280 220 305 200 Q280 180 255 200" fill="none" stroke="#06B6D4" strokeWidth="1.5" />
                    <line x1="255" y1="200" x2="305" y2="200" stroke="#06B6D4" strokeWidth="1.5" />
                    
                    {/* User profile card */}
                    <rect x="60" y="150" width="40" height="30" rx="4" fill="#10B981" />
                    <circle cx="70" cy="160" r="5" fill="white" />
                    <rect x="65" y="170" width="10" height="2" rx="1" fill="white" />
                    <rect x="65" y="174" width="15" height="2" rx="1" fill="white" />
                    
                    {/* Document/Files */}
                    <rect x="300" y="150" width="35" height="45" rx="3" fill="#8B5CF6" />
                    <rect x="305" y="155" width="25" height="2" rx="1" fill="white" />
                    <rect x="305" y="160" width="20" height="2" rx="1" fill="white" />
                    <rect x="305" y="165" width="15" height="2" rx="1" fill="white" />
                    <rect x="305" y="175" width="25" height="2" rx="1" fill="white" />
                    <rect x="305" y="180" width="20" height="2" rx="1" fill="white" />
                    
                    {/* Connection lines */}
                    <path d="M145 190 Q170 180 195 190" stroke="rgba(59, 130, 246, 0.4)" strokeWidth="2" fill="none" strokeDasharray="5,3" />
                    <path d="M245 190 Q270 180 255 190" stroke="rgba(6, 182, 212, 0.4)" strokeWidth="2" fill="none" strokeDasharray="5,3" />
                    <path d="M100 170 Q150 160 180 170" stroke="rgba(16, 185, 129, 0.4)" strokeWidth="2" fill="none" strokeDasharray="5,3" />
                    <path d="M220 170 Q270 160 300 170" stroke="rgba(139, 92, 246, 0.4)" strokeWidth="2" fill="none" strokeDasharray="5,3" />
                    
                    {/* Floating security elements */}
                    <circle cx="80" cy="120" r="4" fill="#10B981" />
                    <circle cx="320" cy="120" r="4" fill="#06B6D4" />
                    <circle cx="80" cy="280" r="4" fill="#8B5CF6" />
                    <circle cx="320" cy="280" r="4" fill="#F59E0B" />
                    
                    {/* Gear/Settings */}
                    <circle cx="200" cy="80" r="15" fill="rgba(59, 130, 246, 0.1)" />
                    <circle cx="200" cy="80" r="8" fill="transparent" stroke="#3B82F6" strokeWidth="2" />
                    <circle cx="200" cy="80" r="3" fill="#3B82F6" />
                    
                    {/* SECURE label */}
                    <rect x="160" y="40" width="80" height="25" rx="6" fill="#1E40AF" />
                    <text x="200" y="58" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">SECURE</text>
                  </svg>
                </div>
                
                <div className="space-y-4">
                  <h2 className="text-4xl font-bold text-blue-600 dark:text-blue-400">SECURE</h2>
                  <p className="text-xl text-gray-600 dark:text-gray-300">IoT Dashboard</p>
                  <p className="text-lg text-gray-500 dark:text-gray-400 leading-relaxed">
                    Monitor and control your IoT devices with enterprise-grade security and real-time analytics.
                  </p>
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Right Side - Form */}
          <motion.div 
            className="lg:w-1/2 bg-gradient-to-br from-blue-500 to-blue-600 dark:from-blue-700 dark:to-blue-800 p-8 lg:p-12 flex items-center justify-center relative overflow-hidden"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Background Pattern for form side */}
            <div className="absolute inset-0 bg-blue-600 dark:bg-blue-800 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              }}></div>
            </div>

            <div className="relative z-10 w-full max-w-md">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <h1 className="text-4xl font-bold text-white mb-2">
                  Welcome!
                </h1>
                <p className="text-blue-100 dark:text-blue-200 mb-8">
                  {isSignUp ? 'Create your account to get started' : 'Sign in to access your dashboard'}
                </p>
              </motion.div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Sign Up Fields */}
                {isSignUp && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-4"
                  >
                    <div>
                      <Input
                        name="name"
                        type="text"
                        placeholder="Your name"
                        value={formData.name}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-white dark:bg-gray-700 border-0 rounded-xl focus:ring-2 focus:ring-white focus:bg-blue-50 dark:focus:bg-gray-600 transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-lg"
                      />
                      {errors.name && <p className="text-red-300 text-sm mt-1">{errors.name}</p>}
                    </div>

                    <div>
                      <Input
                        name="email"
                        type="email"
                        placeholder="Your e-mail"
                        value={formData.email}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-white dark:bg-gray-700 border-0 rounded-xl focus:ring-2 focus:ring-white focus:bg-blue-50 dark:focus:bg-gray-600 transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-lg"
                      />
                      {errors.email && <p className="text-red-300 text-sm mt-1">{errors.email}</p>}
                    </div>

                    <div>
                      <Input
                        name="username"
                        type="text"
                        placeholder="Choose a username"
                        value={formData.username}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-white dark:bg-gray-700 border-0 rounded-xl focus:ring-2 focus:ring-white focus:bg-blue-50 dark:focus:bg-gray-600 transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-lg"
                      />
                      {errors.username && <p className="text-red-300 text-sm mt-1">{errors.username}</p>}
                    </div>
                  </motion.div>
                )}

                {/* Sign In Fields */}
                {!isSignUp && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    transition={{ duration: 0.3 }}
                  >
                    <Input
                      name="username"
                      type="text"
                      placeholder="Username"
                      value={formData.username}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-white dark:bg-gray-700 border-0 rounded-xl focus:ring-2 focus:ring-white focus:bg-blue-50 dark:focus:bg-gray-600 transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-lg"
                    />
                    {errors.username && <p className="text-red-300 text-sm mt-1">{errors.username}</p>}
                  </motion.div>
                )}

                {/* Password Field */}
                <div className="relative">
                  <Input
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 pr-12 bg-white dark:bg-gray-700 border-0 rounded-xl focus:ring-2 focus:ring-white focus:bg-blue-50 dark:focus:bg-gray-600 transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-lg"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center justify-center w-6 h-6 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors duration-200"
                  >
                    {showPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                  {errors.password && <p className="text-red-300 text-sm mt-1">{errors.password}</p>}
                </div>

                {/* Confirm Password for Sign Up */}
                {isSignUp && (
                  <div className="relative">
                    <Input
                      name="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="Confirm password"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 pr-12 bg-white dark:bg-gray-700 border-0 rounded-xl focus:ring-2 focus:ring-white focus:bg-blue-50 dark:focus:bg-gray-600 transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-lg"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center justify-center w-6 h-6 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors duration-200"
                    >
                      {showConfirmPassword ? (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                    {errors.confirmPassword && <p className="text-red-300 text-sm mt-1">{errors.confirmPassword}</p>}
                  </div>
                )}

                {/* Password Strength Indicator */}
                {(isSignUp || formData.password) && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-blue-700 dark:bg-blue-800 rounded-lg p-4 border border-blue-400 dark:border-blue-600"
                  >
                    <div className="flex items-center mb-2">
                      <span className="text-sm font-medium text-blue-100 dark:text-blue-200">
                        Password strength
                      </span>
                      <div className="ml-auto flex space-x-1">
                        {[1, 2, 3, 4, 5].map((i) => (
                          <div
                            key={i}
                            className={`w-6 h-1 rounded-full transition-all duration-200 ${
                              Object.values(passwordValidation.requirements).filter(Boolean).length >= i
                                ? 'bg-yellow-400'
                                : 'bg-blue-400 dark:bg-blue-600'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <div className="text-xs text-blue-100 dark:text-blue-200 space-y-1">
                      <div className={`flex items-center ${passwordValidation.requirements.length ? 'text-yellow-300 dark:text-yellow-400' : 'text-blue-200 dark:text-blue-300'}`}>
                        <span className="mr-2">{passwordValidation.requirements.length ? '✓' : '○'}</span>
                        At least 8 characters
                      </div>
                      <div className={`flex items-center ${passwordValidation.requirements.uppercase ? 'text-yellow-300 dark:text-yellow-400' : 'text-blue-200 dark:text-blue-300'}`}>
                        <span className="mr-2">{passwordValidation.requirements.uppercase ? '✓' : '○'}</span>
                        One uppercase letter
                      </div>
                      <div className={`flex items-center ${passwordValidation.requirements.lowercase ? 'text-yellow-300 dark:text-yellow-400' : 'text-blue-200 dark:text-blue-300'}`}>
                        <span className="mr-2">{passwordValidation.requirements.lowercase ? '✓' : '○'}</span>
                        One lowercase letter
                      </div>
                      <div className={`flex items-center ${passwordValidation.requirements.number ? 'text-yellow-300 dark:text-yellow-400' : 'text-blue-200 dark:text-blue-300'}`}>
                        <span className="mr-2">{passwordValidation.requirements.number ? '✓' : '○'}</span>
                        One number
                      </div>
                      <div className={`flex items-center ${passwordValidation.requirements.special ? 'text-yellow-300 dark:text-yellow-400' : 'text-blue-200 dark:text-blue-300'}`}>
                        <span className="mr-2">{passwordValidation.requirements.special ? '✓' : '○'}</span>
                        One special character
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Submit Buttons */}
                <div className="flex space-x-4">
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="flex-1 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    {isLoading ? 'Loading...' : (isSignUp ? 'Create account' : 'Sign in')}
                  </Button>
                  <Button
                    type="button"
                    onClick={() => setIsSignUp(!isSignUp)}
                    variant="outline"
                    className="flex-1 py-3 border-2 border-white text-white hover:bg-white hover:text-blue-600 dark:hover:bg-gray-100 dark:hover:text-blue-700 rounded-xl transition-all duration-200 bg-transparent"
                  >
                    {isSignUp ? 'Sign in' : 'Create account'}
                  </Button>
                </div>

                {/* Demo Credentials */}
                {/* {!isSignUp && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.5 }}
                    className="mt-6 p-4 bg-blue-700 dark:bg-blue-800 rounded-lg border border-blue-400 dark:border-blue-600"
                  >
                    <h4 className="font-semibold text-blue-100 dark:text-blue-200 mb-2">Demo Credentials:</h4>
                    <div className="text-sm text-blue-200 dark:text-blue-300">
                      <p><strong>Username:</strong> jelly</p>
                      <p><strong>Password:</strong> Jelly123#</p>
                    </div>
                  </motion.div>
                )} */}

                {errors.general && (
                  <p className="text-red-300 text-sm text-center">{errors.general}</p>
                )}
              </form>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
