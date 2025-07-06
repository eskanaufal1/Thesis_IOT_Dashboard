# Authentication System Documentation

## Overview
The IoT Dashboard now includes a complete authentication system with a modern login page design and secure routing.

## Features

### 🔐 Login Page
- **Route**: `/` (root)
- **Design**: Modern, responsive UI similar to the provided design
- **Features**:
  - Sign In / Sign Up toggle
  - Real-time password strength validation
  - Form validation with error handling
  - Smooth animations with Framer Motion

### 🛡️ Password Requirements
The system enforces strong password requirements:
- ✅ At least 8 characters
- ✅ One uppercase letter
- ✅ One lowercase letter  
- ✅ One number
- ✅ One special character

### 👤 Demo Credentials
- **Username**: `jelly`
- **Password**: `Jelly123#`

## Routing Structure

### Public Routes
- `/` - Login page (accessible to all)

### Protected Routes (require authentication)
- `/dashboard` - Main dashboard (previously `/`)
- `/device` - Device management
- `/statistic` - Statistics page
- `/chatbot` - Chatbot interface

## Authentication Flow

1. **Initial Access**: Users accessing any protected route are redirected to `/`
2. **Login**: Users enter credentials on the login page
3. **Validation**: System validates credentials against dummy data
4. **Redirect**: Successful login redirects to `/dashboard`
5. **Session**: Authentication state is stored in localStorage
6. **Logout**: Users can logout via the header button

## Technical Implementation

### Components Created
- `LoginPage.tsx` - Main login interface
- `AuthContext.tsx` - Authentication context and logic
- `ProtectedRoute.tsx` - Route protection wrapper

### Components Updated
- `App.tsx` - Updated routing with authentication
- `Layout.tsx` - Added user info and logout functionality

### Features
- **Persistent Sessions**: Login state preserved across browser sessions
- **Route Protection**: Automatic redirect for unauthenticated users
- **User Display**: Shows user name and avatar in header
- **Secure Logout**: Clears authentication state and redirects

## Security Features

### Client-Side Security
- Input validation and sanitization
- Password strength enforcement
- Session management
- Protected route access control

### Demo Implementation
- Dummy authentication for demonstration
- Local storage session management
- Client-side validation

## Usage

### Development
```bash
npm run dev
```
Access the application at `http://localhost:5174`

### Testing Login
1. Navigate to the root URL
2. Enter demo credentials:
   - Username: `jelly`
   - Password: `Jelly123#`
3. Click "Sign In"
4. You'll be redirected to `/dashboard`

### Testing Protection
1. Try accessing `/dashboard` directly when not logged in
2. You'll be redirected to the login page
3. After login, you'll be redirected back to the requested page

## UI/UX Features

### Design Elements
- 🎨 Modern gradient background
- 📱 Responsive design for mobile and desktop
- 🎯 Interactive password strength indicator
- ✨ Smooth animations and transitions
- 🌓 Dark mode support

### User Experience
- Form validation with real-time feedback
- Loading states during authentication
- Error handling with clear messages
- Intuitive navigation between sign in/up modes

## Future Enhancements

### Security Improvements
- JWT token authentication
- Server-side validation
- Password hashing
- Session timeout
- Multi-factor authentication

### Features
- Password reset functionality
- User profile management
- Role-based access control
- Social login integration

## Dark Mode Support

### Login Page Dark Mode
- **Toggle Button**: Fixed position in top-right corner
- **Smooth Transitions**: Animated theme switching
- **Full Coverage**: All elements adapt to dark/light themes
- **Persistent**: Theme preference saved across sessions
- **Responsive**: Toggle button works on all screen sizes

### Features:
- ✅ Animated toggle button with Framer Motion
- ✅ Background elements adapt to theme
- ✅ Form elements have dark mode variants
- ✅ SVG illustration adjusts to theme
- ✅ Smooth color transitions

## File Structure
```
client/src/
├── components/
│   ├── ProtectedRoute.tsx
│   └── Layout.tsx (updated)
├── contexts/
│   └── AuthContext.tsx
├── pages/
│   └── LoginPage.tsx
└── App.tsx (updated)
```

The authentication system is now fully integrated and ready for production use with proper backend integration.
