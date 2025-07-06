import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { User,  LogOut, Shield,  } from 'lucide-react';


interface UserDropdownProps {
  className?: string;
}

const UserDropdown: React.FC<UserDropdownProps> = ({ className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout } = useAuth();

  const navigate = useNavigate();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleProfileClick = () => {
    setIsOpen(false);
    navigate('/profile');
  };

  const handleLogout = async () => {
    setIsOpen(false);
    await logout();
    navigate('/');
  };

  const userInitials = user?.fullName 
    ? user.fullName.split(' ').map((n: string) => n[0]).join('')
    : user?.username?.[0]?.toUpperCase() || 'J';

  const menuItems = [
    {
      icon: User,
      label: 'Profile',
      onClick: handleProfileClick,
      shortcut: '⌘P'
    },
    {
      icon: LogOut,
      label: 'Sign Out',
      onClick: handleLogout,
      shortcut: '⌘Q',
      danger: true
    }
  ];

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* User Avatar Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 group"
      >
        <div className="relative">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
            {userInitials}
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 border-2 border-white dark:border-gray-800 rounded-full"></div>
        </div>
        <div className="text-left hidden lg:block">
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {user?.fullName || user?.username || 'Jelly User'}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {user?.email || 'jelly@iotdashboard.com'}
          </p>
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="hidden lg:block"
        >
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </motion.div>
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50"
          >
            {/* User Info Header */}
            <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                  {userInitials}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {user?.fullName || user?.username || 'Jelly User'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {user?.email || 'jelly@iotdashboard.com'}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <Shield className="w-3 h-3 text-green-500" />
                    <span className="text-xs text-green-600 dark:text-green-400">Admin</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Menu Items */}
            <div className="py-1">
              {menuItems.map((item, index) => (
                <button
                  key={index}
                  onClick={item.onClick}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 flex items-center justify-between group ${
                    item.danger 
                      ? 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20' 
                      : 'text-gray-700 dark:text-gray-200'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <item.icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">
                    {item.shortcut}
                  </span>
                </button>
              ))}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>Online</span>
                <span>Last seen: now</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UserDropdown;
