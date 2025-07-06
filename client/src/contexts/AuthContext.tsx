import React, { createContext, useContext, useState, useEffect } from 'react';
import { useToastHelpers } from './ToastContext';

const API_BASE_URL = 'http://localhost:8000';

interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  phone?: string;
  company?: string;
  location?: string;
  bio?: string;
  role?: string;
  is_active: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  register: (username: string, email: string, password: string, fullName?: string) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
  updateProfile: (profileData: Partial<User>) => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Password validation function
export const validatePassword = (password: string): { isValid: boolean; requirements: { [key: string]: boolean } } => {
  const requirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
  };

  const isValid = Object.values(requirements).every(req => req);
  
  return { isValid, requirements };
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const toast = useToastHelpers();

  useEffect(() => {
    // Check for stored authentication
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');
    
    if (storedToken && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        // Verify token is still valid by calling /api/auth/me
        verifyToken(storedToken);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        logout();
      }
    }
    setIsLoading(false);
  }, []);

  const verifyToken = async (token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Token verification failed');
      }

      const userData = await response.json();
      setUser(userData);
    } catch (error) {
      console.error('Token verification failed:', error);
      logout();
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
        toast.error('Login Failed', errorData.detail || 'Invalid username or password');
        return false;
      }

      const data = await response.json();
      
      // Store token and user data
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(data.user));
      setUser(data.user);
      
      toast.success('Welcome back!', `Good to see you, ${data.user.full_name || data.user.username}`);
      return true;
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Login Error', 'An unexpected error occurred. Please try again.');
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    toast.info('Logged out', 'You have been successfully logged out.');
  };

  const updateProfile = async (profileData: Partial<User>): Promise<boolean> => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        toast.error('Authentication Error', 'Please log in again');
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Profile update failed' }));
        toast.error('Update Failed', errorData.detail || 'Failed to update profile');
        return false;
      }

      const updatedUser = await response.json();
      setUser(updatedUser);
      localStorage.setItem('auth_user', JSON.stringify(updatedUser));
      
      toast.success('Profile Updated', 'Your profile has been successfully updated');
      return true;
    } catch (error) {
      console.error('Profile update error:', error);
      toast.error('Update Error', 'An unexpected error occurred while updating your profile');
      return false;
    }
  };

  const changePassword = async (currentPassword: string, newPassword: string): Promise<boolean> => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        toast.error('Authentication Error', 'Please log in again');
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Password change failed' }));
        toast.error('Password Change Failed', errorData.detail || 'Failed to change password');
        return false;
      }

      toast.success('Password Changed', 'Your password has been successfully updated');
      return true;
    } catch (error) {
      console.error('Password change error:', error);
      toast.error('Password Change Error', 'An unexpected error occurred while changing your password');
      return false;
    }
  };

  const register = async (username: string, email: string, password: string, fullName?: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          email,
          password,
          full_name: fullName || '',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Registration failed' }));
        toast.error('Registration Failed', errorData.detail || 'Failed to create account');
        return false;
      }

      const data = await response.json();
      toast.success('Account Created', `Welcome ${data.full_name || data.username}! You can now log in.`);
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      toast.error('Registration Error', 'An unexpected error occurred. Please try again.');
      return false;
    }
  };

  const value: AuthContextType = {
    user,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isLoading,
    updateProfile,
    changePassword
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
