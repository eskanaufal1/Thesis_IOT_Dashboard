"""
Example script showing how to use the IoT Dashboard backend with MQTT.
"""

import asyncio
import httpx
import json
import time
from datetime import datetime


async def simulate_iot_device():
    """
    Simulate an IoT device sending sensor data via HTTP API.
    """
    base_url = "http://127.0.0.1:8000"
    
    # Login to get token
    async with httpx.AsyncClient() as client:
        # Use the admin user (created by default)
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = await client.post(f"{base_url}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print("Failed to login as admin")
            return
        
        token_data = response.json()
        access_token = token_data['access_token']
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Simulate sensor data
        sensor_types = ["temperature", "humidity", "pressure", "light"]
        device_ids = ["sensor_001", "sensor_002", "sensor_003"]
        
        for i in range(10):
            for device_id in device_ids:
                for sensor_type in sensor_types:
                    # Generate realistic sensor data
                    if sensor_type == "temperature":
                        value = 20 + (i % 20)  # 20-40°C
                        unit = "°C"
                    elif sensor_type == "humidity":
                        value = 30 + (i % 60)  # 30-90%
                        unit = "%"
                    elif sensor_type == "pressure":
                        value = 1000 + (i % 50)  # 1000-1050 hPa
                        unit = "hPa"
                    else:  # light
                        value = 100 + (i % 900)  # 100-1000 lux
                        unit = "lux"
                    
                    sensor_data = {
                        "device_id": device_id,
                        "sensor_type": sensor_type,
                        "value": value,
                        "unit": unit,
                        "location": f"Room {device_id[-1]}",
                        "metadata_json": json.dumps({
                            "device_model": "IoT-SensorPro",
                            "firmware_version": "1.2.3",
                            "battery_level": 85
                        })
                    }
                    
                    # Send sensor data
                    response = await client.post(
                        f"{base_url}/api/data/sensors",
                        json=sensor_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        print(f"✓ Sent {sensor_type} data from {device_id}: {value}{unit}")
                    else:
                        print(f"✗ Failed to send data: {response.status_code}")
            
            # Wait before next batch
            await asyncio.sleep(1)
        
        # Query the data back
        print("\n=== Querying Recent Data ===")
        response = await client.get(f"{base_url}/api/data/sensors/recent?hours=1", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data)} recent sensor readings")
            
            # Show a sample
            if data:
                sample = data[0]
                print(f"Sample reading: {sample['device_id']} - {sample['sensor_type']}: {sample['value']}{sample['unit']}")
        
        # Get statistics
        print("\n=== Getting Statistics ===")
        response = await client.get(f"{base_url}/api/data/sensors/statistics?hours=1", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"Statistics: {stats}")
        
        # List devices
        print("\n=== Listing Devices ===")
        response = await client.get(f"{base_url}/api/data/sensors/devices", headers=headers)
        if response.status_code == 200:
            devices = response.json()
            print(f"Devices: {devices}")
        
        # List sensor types
        print("\n=== Listing Sensor Types ===")
        response = await client.get(f"{base_url}/api/data/sensors/types", headers=headers)
        if response.status_code == 200:
            types = response.json()
            print(f"Sensor types: {types}")


async def test_mqtt_functionality():
    """
    Test MQTT functionality through the API.
    """
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        # Login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = await client.post(f"{base_url}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print("Failed to login")
            return
        
        token_data = response.json()
        access_token = token_data['access_token']
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Check MQTT status
        print("=== MQTT Status ===")
        response = await client.get(f"{base_url}/api/mqtt/status", headers=headers)
        if response.status_code == 200:
            status = response.json()
            print(f"MQTT Status: {status}")
        
        # Try to publish a message (will fail if no MQTT broker)
        print("\n=== Publishing MQTT Message ===")
        mqtt_message = {
            "topic": "test/sensor",
            "payload": json.dumps({
                "device_id": "test_device",
                "sensor_type": "temperature",
                "value": 25.5,
                "timestamp": datetime.now().isoformat()
            }),
            "qos": 0,
            "retain": False
        }
        
        response = await client.post(f"{base_url}/api/mqtt/publish", json=mqtt_message, headers=headers)
        if response.status_code == 200:
            print("✓ Message published successfully")
        else:
            print(f"✗ Failed to publish message: {response.status_code} - {response.json()}")
        
        # Get MQTT messages
        print("\n=== Getting MQTT Messages ===")
        response = await client.get(f"{base_url}/api/mqtt/messages", headers=headers)
        if response.status_code == 200:
            messages = response.json()
            print(f"Retrieved {len(messages)} MQTT messages")
            if messages:
                print(f"Latest message: {messages[0]}")


async def main():
    """
    Main function to run all tests.
    """
    print("🚀 IoT Dashboard Backend Test Suite")
    print("=" * 50)
    
    print("\n1. Simulating IoT Device Data...")
    await simulate_iot_device()
    
    print("\n2. Testing MQTT Functionality...")
    await test_mqtt_functionality()
    
    print("\n✅ All tests completed!")
    print("\nYou can now:")
    print("- Visit http://127.0.0.1:8000/docs for API documentation")
    print("- Use the authentication endpoints in your frontend")
    print("- Send sensor data via the /api/data/sensors endpoint")
    print("- Monitor MQTT messages if you set up an MQTT broker")


if __name__ == "__main__":
    asyncio.run(main())
