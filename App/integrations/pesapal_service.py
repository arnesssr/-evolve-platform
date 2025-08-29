import requests
from django.conf import settings

BASE_URL = settings.PESAPAL_BASE_URL

# Authentication-> generate the access token
def generate_access_token():
    url = f"{BASE_URL}/api/Auth/RequestToken"
    payload = {
        "consumer_key": settings.PESAPAL_CONSUMER_KEY,
        "consumer_secret": settings.PESAPAL_CONSUMER_SECRET
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("token") if response.status_code == 200 else None

# Register IPN URL
def register_ipn_url(access_token, ipn_url):
    url = f"{BASE_URL}/api/URLSetup/RegisterIPN"
    payload = {
        "url": ipn_url,
        "ipn_notification_type": "GET"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    return requests.post(url, json=payload, headers=headers)

# Fetch all registered IPNs
def get_registered_ipns(access_token):
    url = f"{BASE_URL}/api/URLSetup/GetIpnList"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    return requests.get(url, headers=headers)

# Submit an order and get the redirect URL
def submit_order_request(access_token, payload):
    url = f"{BASE_URL}/api/Transactions/SubmitOrderRequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    # Note: Pesapal payload supports fields documented by the provider.
    # We pass through our description (which may include affiliate markers) as-is.
    return requests.post(url, json=payload, headers=headers)

def get_transaction_status(access_token, tracking_id, merchant_reference):
    url = f"{BASE_URL}/api/Transactions/GetTransactionStatus"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "order_tracking_id": tracking_id,
        "order_merchant_reference": merchant_reference
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json().get("payment_status")  # "COMPLETED", "FAILED", etc.
    else:
        return None


