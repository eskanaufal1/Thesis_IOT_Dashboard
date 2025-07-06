import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';
import { Lock, Settings, Shield, Camera, Save, Edit3 } from 'lucide-react';

const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [profileData, setProfileData] = useState({
    username: user?.username || 'jelly',
    email: user?.email || 'jelly@iotdashboard.com',
    fullName: user?.fullName || 'Jelly User',
    bio: user?.bio || 'IoT Dashboard Administrator',
    location: user?.location || 'San Francisco, CA',
    phone: user?.phone || '+1 (555) 123-4567',
    company: user?.company || 'IoT Solutions Inc.',
    role: user?.role || 'System Administrator'
  });
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = () => {
    // Here you would typically save to a backend
    console.log('Saving profile:', profileData);
    setIsEditing(false);
  };

  const handleSavePassword = () => {
    // Here you would typically save to a backend
    console.log('Changing password');
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    setShowPasswordChange(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Profile Settings</h1>
          <p className="text-gray-600 dark:text-gray-300">Manage your account settings and preferences</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="lg:col-span-1"
          >
            <Card className="p-6 text-center">
              <div className="relative mb-6">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto">
                  {profileData.fullName.split(' ').map(n => n[0]).join('')}
                </div>
                <button className="absolute bottom-0 right-1/2 transform translate-x-1/2 translate-y-1/2 bg-white dark:bg-gray-800 p-2 rounded-full shadow-lg border-2 border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <Camera className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                </button>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">{profileData.fullName}</h2>
              <p className="text-gray-600 dark:text-gray-300 mb-2">@{profileData.username}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{profileData.role}</p>
              <div className="flex items-center justify-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                <div className="flex items-center space-x-1">
                  <Shield className="w-4 h-4" />
                  <span>Verified</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Settings className="w-4 h-4" />
                  <span>Admin</span>
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Profile Information */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="lg:col-span-2"
          >
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Personal Information</h3>
                <Button
                  onClick={() => setIsEditing(!isEditing)}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>{isEditing ? 'Cancel' : 'Edit'}</span>
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Full Name
                  </label>
                  <Input
                    name="fullName"
                    value={profileData.fullName}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Username
                  </label>
                  <Input
                    name="username"
                    value={profileData.username}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Email Address
                  </label>
                  <Input
                    name="email"
                    type="email"
                    value={profileData.email}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <Input
                    name="phone"
                    value={profileData.phone}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Company
                  </label>
                  <Input
                    name="company"
                    value={profileData.company}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Location
                  </label>
                  <Input
                    name="location"
                    value={profileData.location}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full"
                  />
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Bio
                </label>
                <textarea
                  name="bio"
                  value={profileData.bio}
                  onChange={(e) => setProfileData(prev => ({ ...prev, bio: e.target.value }))}
                  disabled={!isEditing}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:cursor-not-allowed"
                />
              </div>

              {isEditing && (
                <div className="flex justify-end space-x-3">
                  <Button
                    onClick={() => setIsEditing(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSaveProfile}
                    className="flex items-center space-x-2"
                  >
                    <Save className="w-4 h-4" />
                    <span>Save Changes</span>
                  </Button>
                </div>
              )}
            </Card>
          </motion.div>

          {/* Security Settings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="lg:col-span-3"
          >
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Security Settings</h3>
                <Button
                  onClick={() => setShowPasswordChange(!showPasswordChange)}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <Lock className="w-4 h-4" />
                  <span>Change Password</span>
                </Button>
              </div>

              {showPasswordChange && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"
                >
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Current Password
                    </label>
                    <Input
                      type="password"
                      name="currentPassword"
                      value={passwordData.currentPassword}
                      onChange={handlePasswordChange}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      New Password
                    </label>
                    <Input
                      type="password"
                      name="newPassword"
                      value={passwordData.newPassword}
                      onChange={handlePasswordChange}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Confirm Password
                    </label>
                    <Input
                      type="password"
                      name="confirmPassword"
                      value={passwordData.confirmPassword}
                      onChange={handlePasswordChange}
                      className="w-full"
                    />
                  </div>
                </motion.div>
              )}

              {showPasswordChange && (
                <div className="flex justify-end space-x-3">
                  <Button
                    onClick={() => setShowPasswordChange(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSavePassword}
                    className="flex items-center space-x-2"
                  >
                    <Save className="w-4 h-4" />
                    <span>Update Password</span>
                  </Button>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Account Status</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Account Status</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">Active</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Two-Factor Auth</span>
                      <span className="text-sm font-medium text-yellow-600 dark:text-yellow-400">Disabled</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Last Login</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Today</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Permissions</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Dashboard Access</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">Granted</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Device Control</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">Granted</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">System Admin</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">Granted</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
