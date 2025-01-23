import requests

# Replace these with your actual Cloudflare API credentials
AUTH_EMAIL = "email@email.com"
AUTH_KEY = "your_auth_key_here"
ACCOUNT_ID = "Cloudflare Account ID"
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}"


def search_user_by_email(email):
    """Search for a Cloudflare Zero Trust user by email."""
    url = f"{BASE_URL}/access/users"
    headers = {
        "X-Auth-Email": AUTH_EMAIL,
        "X-Auth-Key": AUTH_KEY,
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, params={"email": email})
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success", False):
            print(f"Failed to retrieve user: {data.get('errors')}")
            return None
        
        users = data.get("result", [])
        if not users:
            print("No user found with that email address.")
            return None
        
        return users[0]  # Return the first user found
    except requests.exceptions.RequestException as e:
        print(f"Error while querying user by email: {e}")
        return None

def get_device_list():
    """Retrieve the list of devices in Cloudflare Zero Trust."""
    url = f"{BASE_URL}/devices"
    headers = {
        "X-Auth-Email": AUTH_EMAIL,
        "X-Auth-Key": AUTH_KEY,
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success", False):
            print(f"Failed to retrieve device list: {data.get('errors')}")
            return []
        
        return data.get("result", [])
    except requests.exceptions.RequestException as e:
        print(f"Error while querying device list: {e}")
        return []

def find_active_device(user_email, devices):
    """Find the active device ID for a user based on email."""
    for device in devices:
        user_info = device.get("user", {})
        if user_info.get("email") == user_email:
            return device.get("id")
    return None

def get_device_details(device_id):
    """Query Cloudflare Zero Trust API for device details."""
    url = f"{BASE_URL}/devices/{device_id}"
    headers = {
        "X-Auth-Email": AUTH_EMAIL,
        "X-Auth-Key": AUTH_KEY,
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success", False):
            print(f"Failed to retrieve device details: {data.get('errors')}")
            return
        
        device_details = data.get("result", {})
        print("\nDevice Details:")
        print(f"ID: {device_details.get('id')}")
        print(f"Name: {device_details.get('name')}")
        print(f"OS: {device_details.get('device_type')}")
        print(f"Status: {device_details.get('status')}")
        print(f"Tunnel Type: {device_details.get('tunnel_type')}")
        print(f"Last Seen: {device_details.get('last_seen')}")
        user_info = device_details.get('user', {})
        user_email = user_info.get('email', 'Not available')
        print(f"User Email: {user_email}")
    except requests.exceptions.RequestException as e:
        print(f"Error while querying device details: {e}")

def get_fleet_status(device_id):
    """Query Cloudflare Zero Trust API for fleet status, live stats for the past 60 minutes"""
    url = f"{BASE_URL}/dex/devices/{device_id}/fleet-status/live?since_minutes=60"
    headers = {
        "X-Auth-Email": AUTH_EMAIL,
        "X-Auth-Key": AUTH_KEY,
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success", False):
            print(f"Failed to retrieve fleet status: {data.get('errors')}")
            return
        
        fleet_status = data.get("result", {})
        print("\nFleet Status:")
        for key, value in fleet_status.items():
            print(f"{key}: {value}")
    except requests.exceptions.RequestException as e:
        print(f"Error while querying fleet status: {e}")

def main():
    email = input("Enter the user's email address: ").strip()
    if not email:
        print("Email address is required.")
        return

    # Search for the user by email
    user = search_user_by_email(email)
    if not user:
        return
    
    print(f"User found: {user['email']}")

    # Retrieve the list of devices
    devices = get_device_list()
    if not devices:
        print("No devices found.")
        return

    # Find the active device for the user
    active_device_id = find_active_device(email, devices)
    if not active_device_id:
        print("No active device found for this user.")
        return

    print(f"Active Device ID: {active_device_id}")

    # Query device details
    get_device_details(active_device_id)

    # Query fleet status
    get_fleet_status(active_device_id)

if __name__ == "__main__":
    main()