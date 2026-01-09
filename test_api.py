#!/usr/bin/env python3
"""Test script to check API response times"""
import requests
import time

def test_api_endpoint(url, name):
    """Test an API endpoint and measure response time"""
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        elapsed = time.time() - start
        print(f"{name}: {response.status_code} in {elapsed:.2f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"  Data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        return True
    except requests.Timeout:
        print(f"{name}: TIMEOUT after 5s")
        return False
    except requests.ConnectionError as e:
        print(f"{name}: CONNECTION ERROR - {e}")
        return False
    except Exception as e:
        print(f"{name}: ERROR - {e}")
        return False

if __name__ == "__main__":
    base_url = "http://localhost:5000"
    
    print("Testing API endpoints...")
    print("-" * 50)
    
    endpoints = [
        ("/api/temps_named", "Temps Named"),
        ("/api/status", "Status"),
        ("/api/sensors", "Sensors"),
    ]
    
    for endpoint, name in endpoints:
        test_api_endpoint(f"{base_url}{endpoint}", name)
        print()
        time.sleep(0.5)
    
    print("-" * 50)
    print("Test complete")
