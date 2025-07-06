#!/usr/bin/env python3
"""
Test script to verify that the IoT Dashboard Backend installation is working correctly.
"""
import sys
import importlib


def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        "main",
        "config.database",
        "models.database",
        "models.schemas",
        "services.mqtt_service",
        "services.socketio_service",
        "services.database_service",
        "fastapi",
        "uvicorn",
        "paho.mqtt.client",
        "sqlalchemy",
        "socketio",
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} imports failed:")
        for module in failed_imports:
            print(f"  - {module}")
        return False
    else:
        print(f"\n🎉 All {len(modules_to_test)} modules imported successfully!")
        return True


def test_package_structure():
    """Test that the package structure is correct."""
    print("\n📦 Testing package structure...")
    
    try:
        import main
        if hasattr(main, 'app'):
            print("✅ FastAPI app found in main module")
        else:
            print("❌ FastAPI app not found in main module")
            return False
            
        if hasattr(main, 'main'):
            print("✅ main() function found in main module")
        else:
            print("❌ main() function not found in main module")
            return False
        
        print("🎉 Package structure is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Package structure test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting IoT Dashboard Backend Installation Test")
    print("=" * 50)
    
    test_results = []
    
    # Test imports
    test_results.append(test_imports())
    
    # Test package structure
    test_results.append(test_package_structure())
    
    print("\n" + "=" * 50)
    if all(test_results):
        print("🎉 ALL TESTS PASSED! Installation is working correctly.")
        print("You can now start the server with: uv run iot-dashboard")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
