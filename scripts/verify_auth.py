import urllib.request
import urllib.parse
import json
import uuid

BASE_URL = "http://localhost:8000"

def register():
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "password123"
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    json_data = json.dumps(data).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:5173'
    }
    req = urllib.request.Request(url, data=json_data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Register Status: {response.status}")
            cors_header = response.getheader('Access-Control-Allow-Origin')
            print(f"CORS Header: {cors_header}")
            if cors_header != 'http://localhost:5173':
                print("WARNING: CORS Header missing or incorrect!")
            print(f"Register Response: {response.read().decode('utf-8')}")
            return username, password
    except urllib.error.HTTPError as e:
        print(f"Register Failed: {e.code}")
        print(f"Error Content: {e.read().decode('utf-8')}")
        return None, None

def login(username, password):
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({
        "username": username,
        "password": password
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Login Status: {response.status}")
            print(f"Login Response: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"Login Failed: {e.code}")
        print(f"Error Content: {e.read().decode('utf-8')}")

if __name__ == "__main__":
    print("Testing Registration...")
    u, p = register()
    if u:
        print("\nTesting Login...")
        login(u, p)
