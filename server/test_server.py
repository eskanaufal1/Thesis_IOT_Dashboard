#!/usr/bin/env python3
"""
Test script to verify the server can start without errors.
"""
import subprocess
import sys
import time
import requests
from pathlib import Path

def test_server_startup():
    """Test that the server can start and respond to basic requests."""
    print("🧪 Testing server startup...")
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Make sure you're in the server directory.")
        return False
    
    # Start the server in the background
    try:
        print("🚀 Starting server...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "127.0.0.1", "--port", "8001"  # Use different port for testing
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a few seconds for the server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test if server is responding
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is responding to health checks!")
                result = True
            else:
                print(f"❌ Server responded with status code: {response.status_code}")
                result = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to server: {e}")
            result = False
        
        # Stop the server
        process.terminate()
        process.wait(timeout=5)
        print("🛑 Server stopped")
        
        return result
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("📦 Testing imports...")
    
    try:
        import main
        print("✅ main module imported successfully")
        
        from services.mqtt_service import MQTTService
        print("✅ MQTT service imported successfully")
        
        from services.socketio_service import SocketIOService
        print("✅ Socket.IO service imported successfully")
        
        from models.database import Base
        print("✅ Database models imported successfully")
        
        from config.database import engine
        print("✅ Database config imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Testing IoT Dashboard Backend Server...\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Server Startup", test_server_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        results.append(test_func())
    
    print(f"\n{'='*50}")
    if all(results):
        print("🎉 All tests passed! Server is ready to run.")
        print("\nTo start the server:")
        print("1. Run: run_dev.bat (Windows)")
        print("2. Or: python -m uvicorn main:app --reload")
        print("3. Visit: http://localhost:8000/docs for API documentation")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
