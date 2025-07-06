import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  username: string;
  name: string;
  fullName?: string;
  email?: string;
  bio?: string;
  location?: string;
  phone?: string;
  company?: string;
  role?: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Dummy user data
const DUMMY_USER = {
  username: 'jelly',
  password: 'Jelly123#',
  name: 'Jelly User',
  fullName: 'Jelly User',
  email: 'jelly@iotdashboard.com',
  bio: 'IoT Dashboard Administrator',
  location: 'San Francisco, CA',
  phone: '+1 (555) 123-4567',
  company: 'IoT Solutions Inc.',
  role: 'System Administrator'
};

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

  useEffect(() => {
    // Check for stored authentication
    const storedUser = localStorage.getItem('auth_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Check credentials
    if (username === DUMMY_USER.username && password === DUMMY_USER.password) {
      const userData = { username: DUMMY_USER.username, name: DUMMY_USER.name };
      setUser(userData);
      localStorage.setItem('auth_user', JSON.stringify(userData));
      return true;
    }
    
    return false;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('auth_user');
  };

  const value: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    isLoading
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
