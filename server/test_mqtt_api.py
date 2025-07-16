#!/usr/bin/env python3
"""
Test script to verify the MQTT broker management API endpoints work correctly.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_mqtt_broker_api():
    """Test the MQTT broker management API endpoints."""
    
    print("🧪 Testing MQTT Broker Management API")
    print("=" * 50)
    
    # Test 1: Login to get token
    print("\n1. Testing Login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Login successful! Token: {token[:20]}...")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 2: Get broker status
    print("\n2. Testing Broker Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/mqtt-brokers/status", headers=headers)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Broker Status: {json.dumps(status, indent=2)}")
        else:
            print(f"❌ Status failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Status error: {e}")
    
    # Test 3: List brokers
    print("\n3. Testing List Brokers...")
    try:
        response = requests.get(f"{BASE_URL}/api/mqtt-brokers/brokers", headers=headers)
        if response.status_code == 200:
            brokers = response.json()
            print(f"✅ Brokers Found: {len(brokers)} brokers")
            for broker in brokers:
                print(f"   - {broker['broker_name']}: {broker['broker_host']}:{broker['broker_port']}")
        else:
            print(f"❌ List brokers failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ List brokers error: {e}")
    
    # Test 4: Create a new broker
    print("\n4. Testing Create Broker...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    broker_data = {
        "broker_name": f"Test Broker {timestamp}",
        "broker_host": "test.mosquitto.org",
        "broker_port": 1883,
        "username": "",
        "password": ""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/mqtt-brokers/brokers", json=broker_data, headers=headers)
        if response.status_code in [200, 201]:
            new_broker = response.json()
            print(f"✅ Broker created: {new_broker['broker_name']} (ID: {new_broker['id']})")
            broker_id = new_broker["id"]
        else:
            print(f"❌ Create broker failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Create broker error: {e}")
        return
    
    # Test 5: Control broker connection (connect)
    print("\n5. Testing Broker Connection Control...")
    try:
        control_data = {"action": "connect"}
        response = requests.post(f"{BASE_URL}/api/mqtt-brokers/brokers/{broker_id}/control", json=control_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Connection control: {result['message']}")
        else:
            print(f"❌ Connection control failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection control error: {e}")
    
    # Test 6: Get updated status
    print("\n6. Testing Updated Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/mqtt-brokers/status", headers=headers)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Updated Status: {json.dumps(status, indent=2)}")
        else:
            print(f"❌ Updated status failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Updated status error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 MQTT Broker API Test Complete!")

if __name__ == "__main__":
    test_mqtt_broker_api()
