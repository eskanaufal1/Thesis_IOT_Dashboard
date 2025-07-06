# IoT Dashboard

A modern, full-stack IoT dashboard application built with React, TypeScript, and FastAPI. This project provides a comprehensive platform for monitoring IoT devices, viewing analytics, and managing user authentication.

## 🚀 Features

### Frontend (React + TypeScript)
- **Modern UI/UX**: Clean, responsive design with dark mode support
- **Authentication**: Secure login system with JWT tokens
- **Real-time Data**: Live updates for device status and metrics
- **Interactive Charts**: Beautiful data visualization with Chart.js
- **Profile Management**: User profile editing and password changes
- **Code Splitting**: Lazy loading for optimal performance
- **Toast Notifications**: User-friendly feedback system
- **Error Boundaries**: Graceful error handling
- **Loading States**: Skeleton screens and loading indicators

### Backend (FastAPI + Python)
- **FastAPI**: High-performance async API framework
- **Authentication**: JWT-based authentication with password hashing
- **Database**: SQLAlchemy ORM with SQLite
- **Real-time**: Socket.IO for real-time communication
- **MQTT**: Support for IoT device communication
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Modern Python**: Type hints and async/await patterns

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Chart.js** - Data visualization
- **Lucide React** - Icon library
- **React Router** - Client-side routing

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **Pydantic** - Data validation
- **Python-Jose** - JWT handling
- **Passlib** - Password hashing
- **Socket.IO** - Real-time communication
- **MQTT** - IoT messaging

## 📦 Installation

### Prerequisites
- **Node.js** (v18 or higher)
- **Python** (v3.11 or higher)
- **uv** (Python package manager)

### 1. Clone the repository
```bash
git clone <repository-url>
cd Thesis_IOT_Dashboard
```

### 2. Backend Setup
```bash
# Navigate to server directory
cd server

# Install dependencies using uv
uv sync

# Start the development server
uv run python -m fastapi dev main.py --port 8000
```

### 3. Frontend Setup
```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔐 Authentication

The application uses a demo authentication system:

**Demo User Credentials:**
- Username: `jelly`
- Password: `Jelly123#`

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## 📱 Features Overview

### Dashboard
- Real-time device status monitoring
- Key performance indicators (KPIs)
- Interactive charts and graphs
- Quick action buttons

### Device Management
- Device listing and status
- Device configuration
- Historical data viewing
- Device control interface

### Statistics & Analytics
- Performance metrics visualization
- Historical trend analysis
- Data export capabilities
- Custom reporting

### User Profile
- Profile information editing
- Password change functionality
- Account settings
- Role and permissions display

### Chatbot
- AI-powered assistance
- Device troubleshooting
- Quick help and support
- Interactive conversations

## 🏗️ Project Structure

```
Thesis_IOT_Dashboard/
├── client/                 # Frontend React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── contexts/      # React contexts (Auth, Theme, Toast)
│   │   ├── pages/         # Page components
│   │   └── assets/        # Static assets
│   ├── public/            # Public assets
│   └── package.json       # Frontend dependencies
├── server/                # Backend FastAPI application
│   ├── api/              # API route handlers
│   ├── models/           # Database models and schemas
│   ├── services/         # Business logic services
│   ├── config/           # Configuration files
│   └── pyproject.toml    # Backend dependencies
└── README.md             # This file
```

## 🚀 Development

### Frontend Development
```bash
cd client
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend Development
```bash
cd server
uv run python -m fastapi dev main.py    # Start development server
uv run python -m fastapi run main.py    # Start production server
```

## 🎨 Customization

### Theme Configuration
The application supports both light and dark themes. Theme switching is available in the user dropdown menu.

### Environment Variables
Create a `.env` file in the server directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./main.db
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
```

## 📊 Performance Optimizations

- **Code Splitting**: Lazy loading of route components
- **Bundle Optimization**: Vite's built-in optimizations
- **Image Optimization**: Optimized assets and SVGs
- **Caching**: Browser caching strategies
- **Memoization**: React.memo and useMemo for expensive operations

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password security
- **CORS Configuration**: Proper cross-origin resource sharing
- **Input Validation**: Pydantic models for data validation
- **Error Handling**: Secure error messages

## 🧪 Testing

### Frontend Testing
```bash
cd client
npm test              # Run tests
npm run test:coverage # Run tests with coverage
```

### Backend Testing
```bash
cd server
uv run pytest        # Run tests
uv run pytest --cov  # Run tests with coverage
```

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- React team for the excellent framework
- FastAPI team for the high-performance backend framework
- The open-source community for the amazing tools and libraries

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Happy Coding!** 🚀
