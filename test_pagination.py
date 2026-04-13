#!/usr/bin/env python3
import requests

TOKEN = "fc0d416cdf17522aba6642f8465fc0ad141b06e8"
HEADERS = {"Authorization": f"Token {TOKEN}"}

print("Testing pagination fix...")

try:
    response = requests.get("http://localhost:8000/api/v1/rooms/", headers=HEADERS, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Count: {data.get('count', 'N/A')}")
        print(f"Results returned: {len(data.get('results', []))}")
        print("✅ Rooms API working")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:200])

except requests.exceptions.RequestException as e:
    print(f"❌ Connection error: {e}")