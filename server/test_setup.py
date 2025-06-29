#!/usr/bin/env python3
"""
Test script to verify the uv setup and dependencies are working correctly.
"""

def test_imports():
    """Test that all required packages can be imported."""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import paho.mqtt.client as mqtt
        import socketio
        import pydantic
        import dotenv
        import aiomqtt
        import aiofiles
        import passlib
        from jose import jwt
        
        print("✅ All imports successful!")
        print(f"FastAPI: {fastapi.__version__}")
        print(f"SQLAlchemy: {sqlalchemy.__version__}")
        print(f"Pydantic: {pydantic.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_python_version():
    """Test Python version compatibility."""
    import sys
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible (requires 3.11+)")
        return False

def test_environment():
    """Test environment configuration."""
    import os
    from pathlib import Path
    
    env_file = Path('.env')
    env_template = Path('.env.template')
    
    if env_template.exists():
        print("✅ Environment template found")
    else:
        print("❌ Environment template not found")
        return False
        
    if env_file.exists():
        print("✅ Environment file found")
    else:
        print("⚠️  Environment file not found - copy from .env.template")
        
    return True

def main():
    """Run all tests."""
    print("🔍 Testing uv setup for IoT Dashboard Backend...\n")
    
    tests = [
        ("Python Version", test_python_version),
        ("Package Imports", test_imports), 
        ("Environment Setup", test_environment),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        results.append(test_func())
    
    print(f"\n{'='*50}")
    if all(results):
        print("🎉 All tests passed! Setup is working correctly.")
        print("\nNext steps:")
        print("1. Copy .env.template to .env and configure")
        print("2. Run: uv run uvicorn main:app --reload")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
if __name__ == "__main__":
    main()
