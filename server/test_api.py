"""
Test script to verify the backend API endpoints work correctly.
"""

import asyncio
import httpx
import json


async def test_api():
    """Test the API endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        # Test root endpoint
        print("Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"Root response: {response.status_code}, {response.json()}")
        
        # Test health endpoint
        print("\nTesting health endpoint...")
        response = await client.get(f"{base_url}/health")
        print(f"Health response: {response.status_code}, {response.json()}")
        
        # Test user registration
        print("\nTesting user registration...")
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
        response = await client.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"Register response: {response.status_code}")
        if response.status_code == 201:
            print(f"User created: {response.json()}")
        else:
            print(f"Registration failed: {response.json()}")
        
        # Test user login
        print("\nTesting user login...")
        login_data = {
            "username": "testuser",
            "password": "Test123!@#"
        }
        response = await client.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"Login successful: {token_data['user']['username']}")
            access_token = token_data['access_token']
            
            # Test protected endpoint
            print("\nTesting protected endpoint...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{base_url}/api/auth/me", headers=headers)
            print(f"Me response: {response.status_code}, {response.json()}")
            
            # Test MQTT status
            print("\nTesting MQTT status...")
            response = await client.get(f"{base_url}/api/mqtt/status", headers=headers)
            print(f"MQTT status: {response.status_code}, {response.json()}")
            
        else:
            print(f"Login failed: {response.json()}")


if __name__ == "__main__":
    asyncio.run(test_api())
