"""
Simple MQTT broker test using curl-like requests.
"""

import asyncio
import httpx
import json


async def test_mqtt_brokers():
    """Test MQTT broker functionality."""
    
    print("🧪 Testing MQTT Broker API")
    print("=" * 40)
    
    # Test authentication first
    client = httpx.AsyncClient()
    
    try:
        # Login
        print("1. Logging in...")
        login_response = await client.post(
            "http://127.0.0.1:8000/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ Login failed, trying different password...")
            # Try with different password
            login_response = await client.post(
                "http://127.0.0.1:8000/api/auth/login",
                json={"username": "admin", "password": "password"}
            )
            print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
            
            # Test broker creation
            print("\n2. Creating MQTT broker...")
            broker_data = {
                "broker_name": "Test Broker",
                "broker_host": "localhost",
                "broker_port": 1883,
                "username": "test",
                "password": "test"
            }
            
            broker_response = await client.post(
                "http://127.0.0.1:8000/api/mqtt-brokers/brokers",
                json=broker_data,
                headers=headers
            )
            print(f"Broker creation status: {broker_response.status_code}")
            
            if broker_response.status_code == 200:
                broker = broker_response.json()
                print(f"✅ Created broker: {broker['broker_name']}")
                
                # Test broker listing
                print("\n3. Listing brokers...")
                list_response = await client.get(
                    "http://127.0.0.1:8000/api/mqtt-brokers/brokers",
                    headers=headers
                )
                print(f"List status: {list_response.status_code}")
                
                if list_response.status_code == 200:
                    brokers = list_response.json()
                    print(f"✅ Found {len(brokers)} brokers")
                    
                    # Test broker status
                    print("\n4. Checking broker status...")
                    status_response = await client.get(
                        "http://127.0.0.1:8000/api/mqtt-brokers/status",
                        headers=headers
                    )
                    print(f"Status check: {status_response.status_code}")
                    
                    if status_response.status_code == 200:
                        statuses = status_response.json()
                        print(f"✅ Status retrieved for {len(statuses)} brokers")
                        
                        for status in statuses:
                            connected = "🟢" if status["connected"] else "🔴"
                            print(f"  {connected} {status['broker_name']}")
                    else:
                        print(f"❌ Status check failed: {status_response.text}")
                else:
                    print(f"❌ Listing failed: {list_response.text}")
            else:
                print(f"❌ Broker creation failed: {broker_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(test_mqtt_brokers())
