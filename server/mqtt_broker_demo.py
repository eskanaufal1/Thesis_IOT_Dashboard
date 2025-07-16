"""
Test script to demonstrate MQTT broker management functionality.
"""

import asyncio
import json
from typing import Dict, Any
import httpx


class MQTTBrokerDemo:
    """Demo class for MQTT broker management."""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.token = None
        self.client = httpx.AsyncClient()
    
    async def register(self, username: str, email: str, password: str):
        """Register a new user."""
        register_data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/auth/register",
            json=register_data
        )
        
        if response.status_code == 200:
            print(f"✅ Registered user: {username}")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False

    async def login(self, username: str = "admin", password: str = "admin"):
        """Login to get authentication token."""
        login_data = {
            "username": username,
            "password": password
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            print(f"✅ Logged in successfully as {username}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def create_mqtt_broker(self, name: str, host: str, port: int = 1883, 
                                username: str = None, password: str = None):
        """Create a new MQTT broker configuration."""
        broker_data = {
            "broker_name": name,
            "broker_host": host,
            "broker_port": port,
            "username": username,
            "password": password
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/mqtt-brokers/brokers",
            json=broker_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created MQTT broker: {name} ({host}:{port})")
            return data
        else:
            print(f"❌ Failed to create broker: {response.text}")
            return None
    
    async def get_mqtt_brokers(self):
        """Get all MQTT brokers."""
        response = await self.client.get(
            f"{self.base_url}/api/mqtt-brokers/brokers",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            brokers = response.json()
            print(f"📋 Found {len(brokers)} MQTT brokers:")
            for broker in brokers:
                print(f"  - {broker['broker_name']}: {broker['broker_host']}:{broker['broker_port']}")
            return brokers
        else:
            print(f"❌ Failed to get brokers: {response.text}")
            return []
    
    async def get_broker_status(self):
        """Get status of all MQTT brokers."""
        response = await self.client.get(
            f"{self.base_url}/api/mqtt-brokers/status",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            statuses = response.json()
            print(f"📊 MQTT Broker Status:")
            for status in statuses:
                connected = "🟢 Connected" if status["connected"] else "🔴 Disconnected"
                print(f"  - {status['broker_name']}: {connected}")
            return statuses
        else:
            print(f"❌ Failed to get broker status: {response.text}")
            return []
    
    async def control_broker(self, broker_id: int, action: str):
        """Control MQTT broker (connect/disconnect)."""
        control_data = {"action": action}
        
        response = await self.client.post(
            f"{self.base_url}/api/mqtt-brokers/brokers/{broker_id}/control",
            json=control_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            print(f"✅ Broker {broker_id} {action}ed successfully")
            return True
        else:
            print(f"❌ Failed to {action} broker: {response.text}")
            return False
    
    async def create_device(self, broker_id: int, device_name: str, device_id: str, 
                           device_type: str = "sensor"):
        """Create a new device configuration."""
        device_data = {
            "mqtt_broker_id": broker_id,
            "device_name": device_name,
            "device_id": device_id,
            "device_type": device_type,
            "location": "Test Location",
            "description": f"Test device {device_name}"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/mqtt-brokers/devices",
            json=device_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created device: {device_name} ({device_id})")
            return data
        else:
            print(f"❌ Failed to create device: {response.text}")
            return None
    
    async def get_devices(self):
        """Get all devices."""
        response = await self.client.get(
            f"{self.base_url}/api/mqtt-brokers/devices",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            devices = response.json()
            print(f"📱 Found {len(devices)} devices:")
            for device in devices:
                print(f"  - {device['device_name']}: {device['device_id']} ({device['device_type']})")
            return devices
        else:
            print(f"❌ Failed to get devices: {response.text}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main demo function."""
    demo = MQTTBrokerDemo()
    
    try:
        print("🚀 Starting MQTT Broker Management Demo")
        print("=" * 50)
        
        # Try to register and login with demo user
        print("\n0. Setting up demo user...")
        await demo.register("mqttdemo", "mqttdemo@example.com", "demopass123")
        
        # Login
        if not await demo.login("mqttdemo", "demopass123"):
            # Try with admin if demo user fails
            print("Trying with admin user...")
            if not await demo.login("admin", "admin123"):
                print("Trying with different admin password...")
                if not await demo.login("admin", "password"):
                    return
        
        print("\n1. Creating MQTT Brokers...")
        # Create test brokers
        broker1 = await demo.create_mqtt_broker(
            "Local Mosquitto", 
            "localhost", 
            1883, 
            "testuser", 
            "testpass"
        )
        
        broker2 = await demo.create_mqtt_broker(
            "HiveMQ Public", 
            "broker.hivemq.com", 
            1883
        )
        
        broker3 = await demo.create_mqtt_broker(
            "Eclipse Mosquitto", 
            "test.mosquitto.org", 
            1883
        )
        
        print("\n2. Listing MQTT Brokers...")
        brokers = await demo.get_mqtt_brokers()
        
        print("\n3. Checking Broker Status...")
        statuses = await demo.get_broker_status()
        
        print("\n4. Creating Test Devices...")
        if brokers:
            # Create test devices for each broker
            for i, broker in enumerate(brokers[:2]):  # Limit to first 2 brokers
                device = await demo.create_device(
                    broker['id'],
                    f"Test Sensor {i+1}",
                    f"sensor_{i+1:03d}",
                    "temperature"
                )
        
        print("\n5. Listing Devices...")
        devices = await demo.get_devices()
        
        print("\n6. Testing Broker Control...")
        if brokers:
            broker_id = brokers[0]['id']
            print(f"Testing connect/disconnect for broker {broker_id}")
            
            # Try to connect
            await demo.control_broker(broker_id, "connect")
            await asyncio.sleep(2)
            
            # Check status
            await demo.get_broker_status()
            
            # Try to disconnect
            await demo.control_broker(broker_id, "disconnect")
            await asyncio.sleep(2)
            
            # Check status again
            await demo.get_broker_status()
        
        print("\n✅ Demo completed successfully!")
        print("=" * 50)
        print("🎯 Next steps:")
        print("1. Check the Statistics page for MQTT broker controls")
        print("2. Use the API documentation at http://127.0.0.1:8000/docs")
        print("3. Set up real MQTT brokers for production use")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        
    finally:
        await demo.close()


if __name__ == "__main__":
    asyncio.run(main())
