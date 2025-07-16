"""
Test admin login functionality.
"""

import asyncio
import httpx
import json


async def test_admin_login():
    """Test admin login."""
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        # Test admin login
        print("Testing admin login...")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = await client.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Admin login response: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"Admin login successful: {token_data['user']['username']}")
            print(f"Admin role: {token_data['user']['role']}")
            access_token = token_data['access_token']
            
            # Test admin endpoints
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test getting all users (admin only)
            print("\nTesting admin endpoint - get all users...")
            response = await client.get(f"{base_url}/api/auth/users", headers=headers)
            print(f"Get users response: {response.status_code}")
            if response.status_code == 200:
                users = response.json()
                print(f"Found {len(users)} users:")
                for user in users:
                    print(f"  - {user['username']} ({user['role']})")
        else:
            print(f"Admin login failed: {response.json()}")


if __name__ == "__main__":
    asyncio.run(test_admin_login())
