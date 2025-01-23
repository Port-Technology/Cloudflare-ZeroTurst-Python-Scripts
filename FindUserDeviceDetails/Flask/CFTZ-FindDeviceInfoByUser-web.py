from flask import Flask, render_template, request, jsonify
import requests, os

# Replace these with your actual Cloudflare API credentials
AUTH_EMAIL = os.environ.get("CF-email")
AUTH_KEY = os.environ.get("CF-key")
ACCOUNT_ID = os.environ.get("CF-Account")
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}"

app = Flask(__name__)

def search_user_by_email(email):
    """Search for a Cloudflare Zero Trust user by email."""
    url = f"{BASE_URL}/access/users"
    headers = {
        "X-Auth-Email": AUTH_EMAIL,
        "X-Auth-Key": AUTH_KEY,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, params={"email": email})
    response.raise_for_status()
    data = response.json()

    if not data.get("success", False):
        return {"error": data.get("errors")}
    return data.get("result", [])

def get_device_list():
    """Retrieve the list of devices in Cloudflare Zero Trust."""
    url = f"{BASE_URL}/devices"
    headers = {
        "X-Auth-Email": AUTH_EMAIL,
        "X-Auth-Key": AUTH_KEY,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    if not data.get("success", False):
        return {"error": data.get("errors")}
    return data.get("result", [])

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
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    if not data.get("success", False):
        return {"error": data.get("errors")}
    return data.get("result", {})

def get_fleet_status(device_id):
    """Query Cloudflare Zero Trust API for fleet status."""
    url = f"{BASE_URL}/dex/devices/{device_id}/fleet-status/live?since_minutes=60"
    headers = {
        "X-Auth-Email": AUTH_EMAIL,
        "X-Auth-Key": AUTH_KEY,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    if not data.get("success", False):
        return {"error": data.get("errors")}
    return data.get("result", {})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    email = request.form.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Search for the user by email
        users = search_user_by_email(email)
        if not users:
            return jsonify({"error": "User not found"}), 404

        # Retrieve the list of devices
        devices = get_device_list()
        if not devices:
            return jsonify({"error": "No devices found"}), 404

        # Find the active device for the user
        active_device_id = find_active_device(email, devices)
        if not active_device_id:
            return jsonify({"error": "No active device found"}), 404

        # Query device details and fleet status
        device_details = get_device_details(active_device_id)
        fleet_status = get_fleet_status(active_device_id)

        return jsonify({
            "user_email": email,
            "active_device_id": active_device_id,
            "device_details": device_details,
            "fleet_status": fleet_status,
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)