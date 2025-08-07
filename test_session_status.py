import requests
import time

# Base URL
BASE_URL = "https://pimpmycase.onrender.com/api/vending"

# Step 1: Create a Session
def create_session():
    url = f"{BASE_URL}/create-session"
    payload = {
        "machine_id": "10HKNTDOH2BA",
        "location": "Test Location",
        "session_timeout_minutes": 30,
        "metadata": {"test": True}
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("success") and "session_id" in data:
            print("✅ Session created successfully.")
            print("Session ID:", data["session_id"])
            return data["session_id"]
        else:
            print("❌ Failed to create session:", data)
            return None
    except Exception as e:
        print("❌ Error during session creation:", e)
        return None

# Step 2: Check Session Status
def check_session_status(session_id):
    url = f"{BASE_URL}/session/{session_id}/status"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("✅ Session status:")
        print(data)
    except Exception as e:
        print("❌ Error checking session status:", e)

if __name__ == "__main__":
    session_id = create_session()
    if session_id:
        time.sleep(1)  # Short pause before checking status
        check_session_status(session_id)
