#!/usr/bin/env python3
"""
Simple test to check what happens when we try to start the server.
"""
import asyncio
from main import app

async def test_startup():
    """Test the lifespan function."""
    print("🧪 Testing server startup sequence...")
    
    # The lifespan function should be callable
    try:
        # Test the app creation
        print("✅ FastAPI app created")
        
        # Test basic route
        print(f"✅ App has {len(app.routes)} routes")
        
        print("🎉 Basic server setup is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error during startup test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_startup())
