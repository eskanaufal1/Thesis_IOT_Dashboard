#!/usr/bin/env python3
"""
Final status check for the IoT Dashboard Backend server.
"""

def check_server_status():
    """Check the current status of the server setup."""
    print("🏥 IoT Dashboard Backend - Health Check")
    print("=" * 50)
    
    # Check files
    files_to_check = [
        "main.py",
        ".env",
        ".env.template", 
        "requirements.txt",
        "pyproject.toml",
        "run_dev.bat",
        "run_dev.ps1"
    ]
    
    print("\n📁 Files Status:")
    for file in files_to_check:
        try:
            with open(file, 'r') as f:
                print(f"✅ {file}")
        except FileNotFoundError:
            print(f"❌ {file} - Missing")
    
    # Check directories
    dirs_to_check = ["config", "models", "services", "venv"]
    print("\n📂 Directories Status:")
    for dir_name in dirs_to_check:
        import os
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - Missing")
    
    # Check imports
    print("\n📦 Import Status:")
    try:
        from main import app
        print("✅ FastAPI app")
        
        from services.mqtt_service import MQTTService
        print("✅ MQTT service")
        
        from services.socketio_service import SocketIOService  
        print("✅ Socket.IO service")
        
        from models.database import Base
        print("✅ Database models")
        
        from config.database import engine
        print("✅ Database config")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    
    # Check environment
    print("\n🌍 Environment Status:")
    import os
    env_vars = [
        "DATABASE_PATH",
        "MQTT_BROKER_HOST", 
        "MQTT_BROKER_PORT",
        "SECRET_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"⚠️  {var} - Not set (using defaults)")
    
    print("\n" + "=" * 50)
    print("🎯 Ready to start server!")
    print("\n🚀 To start the development server:")
    print("   Windows: run_dev.bat")
    print("   PowerShell: .\\run_dev.ps1") 
    print("   Manual: python -m uvicorn main:app --reload")
    print("\n📚 API Documentation will be available at:")
    print("   http://localhost:8000/docs")
    print("   http://localhost:8000/redoc")

if __name__ == "__main__":
    check_server_status()
