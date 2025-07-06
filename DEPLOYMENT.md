# Deployment Guide

This guide covers different deployment options for the IoT Dashboard application.

## 🚀 Quick Deployment

### Option 1: Local Development
```bash
# Terminal 1 - Backend
cd server
uv run python -m fastapi dev main.py --port 8000

# Terminal 2 - Frontend
cd client
npm run dev
```

### Option 2: Production Build
```bash
# Build frontend
cd client
npm run build

# Serve frontend (using a simple server)
npx serve -s dist -p 3000

# Run backend in production mode
cd server
uv run python -m fastapi run main.py --port 8000
```

## 🐳 Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### 1. Create Docker files

**Frontend Dockerfile** (`client/Dockerfile`):
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Backend Dockerfile** (`server/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "python", "-m", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  frontend:
    build: ./client
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000

  backend:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./main.db
      - SECRET_KEY=your-secret-key-here
    volumes:
      - ./server/main.db:/app/main.db

  mqtt:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
```

### 2. Deploy with Docker Compose
```bash
docker-compose up -d
```

## ☁️ Cloud Deployment

### Vercel (Frontend)

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy Frontend**:
```bash
cd client
vercel --prod
```

3. **Environment Variables**:
Set `VITE_API_URL` to your backend URL in Vercel dashboard.

### Railway (Backend)

1. **Install Railway CLI**:
```bash
npm i -g @railway/cli
```

2. **Deploy Backend**:
```bash
cd server
railway login
railway init
railway up
```

3. **Environment Variables**:
Set the following in Railway dashboard:
- `SECRET_KEY`
- `DATABASE_URL`
- `MQTT_BROKER_HOST`

### Netlify (Frontend)

1. **Build Configuration** (`netlify.toml`):
```toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  VITE_API_URL = "https://your-backend-url.com"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **Deploy**:
```bash
cd client
npm run build
netlify deploy --prod --dir=dist
```

## 🔧 Environment Configuration

### Frontend Environment Variables
Create `client/.env.production`:
```env
VITE_API_URL=https://your-backend-url.com
VITE_MQTT_WS_URL=wss://your-mqtt-broker.com:9001
```

### Backend Environment Variables
Create `server/.env`:
```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///./main.db
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
CORS_ORIGINS=["http://localhost:3000", "https://your-frontend-url.com"]
```

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Configure proper CORS origins
- [ ] Use HTTPS in production
- [ ] Secure database credentials
- [ ] Enable rate limiting
- [ ] Configure proper logging
- [ ] Set up monitoring and alerts
- [ ] Use environment variables for sensitive data
- [ ] Regular security updates

### SSL/TLS Configuration
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring and Analytics

### Application Monitoring
```python
# Add to server/main.py
from fastapi import FastAPI
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    return response
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

## 📈 Performance Optimization

### Frontend Optimization
```javascript
// Preload critical routes
const DashboardPage = lazy(() => 
  import('./pages/DashboardPage').then(module => ({
    default: module.DashboardPage
  }))
);

// Service Worker for caching
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js');
  });
}
```

### Backend Optimization
```python
# Add caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_device_stats(device_id: str):
    # Expensive computation
    return stats

# Database connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_size=10,
    max_overflow=20
)
```

## 🔄 CI/CD Pipeline

### GitHub Actions (`.github/workflows/deploy.yml`)
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          cd client && npm ci
          cd ../server && pip install uv && uv sync
          
      - name: Run tests
        run: |
          cd client && npm test
          cd ../server && uv run pytest
          
      - name: Build
        run: |
          cd client && npm run build
          
      - name: Deploy to production
        # Add your deployment steps here
```

## 📝 Troubleshooting

### Common Issues

1. **CORS Errors**:
   ```python
   # Add to server/main.py
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Database Connection Issues**:
   ```python
   # Ensure database directory exists
   import os
   os.makedirs("./data", exist_ok=True)
   DATABASE_URL = "sqlite:///./data/main.db"
   ```

3. **Build Failures**:
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Logs and Debugging
```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check service status
docker-compose ps
```

## 🔧 Maintenance

### Regular Tasks
- [ ] Update dependencies monthly
- [ ] Monitor application performance
- [ ] Backup database regularly
- [ ] Review security logs
- [ ] Update SSL certificates
- [ ] Monitor disk space and memory usage

### Database Backup
```bash
# SQLite backup
cp server/main.db server/main.db.backup.$(date +%Y%m%d)

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cp server/main.db "${BACKUP_DIR}/main.db.${DATE}"
find "${BACKUP_DIR}" -name "main.db.*" -mtime +7 -delete
```

---

Need help with deployment? Open an issue in the repository or contact the development team.
