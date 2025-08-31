import requests
import logging
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

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
    
    logger.info(f"[PESAPAL] Requesting token from: {url}")
    logger.debug(f"[PESAPAL] Consumer key: {settings.PESAPAL_CONSUMER_KEY[:10]}..." if settings.PESAPAL_CONSUMER_KEY else "[PESAPAL] Consumer key is empty!")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        logger.info(f"[PESAPAL] Token response status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("token")
            if token:
                logger.info("[PESAPAL] Token generated successfully")
                return token
            else:
                logger.error("[PESAPAL] Token not found in response")
                logger.error(f"[PESAPAL] Response: {response.json()}")
        else:
            logger.error(f"[PESAPAL] Failed to generate token. Status: {response.status_code}")
            logger.error(f"[PESAPAL] Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"[PESAPAL] Request error during token generation: {e}")
    except Exception as e:
        logger.error(f"[PESAPAL] Unexpected error during token generation: {e}")
    
    return None

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
    
    logger.info(f"[PESAPAL] Submitting order to: {url}")
    logger.debug(f"[PESAPAL] Order payload: {payload}")
    
    try:
        # Note: Pesapal payload supports fields documented by the provider.
        # We pass through our description (which may include affiliate markers) as-is.
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        logger.info(f"[PESAPAL] Order submission response status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("[PESAPAL] Order submitted successfully")
            logger.debug(f"[PESAPAL] Response: {response.json()}")
        else:
            logger.error(f"[PESAPAL] Order submission failed. Status: {response.status_code}")
            logger.error(f"[PESAPAL] Response: {response.text}")
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"[PESAPAL] Request error during order submission: {e}")
        raise
    except Exception as e:
        logger.error(f"[PESAPAL] Unexpected error during order submission: {e}")
        raise

def _parse_payment_status(payload: dict) -> str | None:
    try:
        # Common variants from providers
        candidates = [
            'payment_status', 'PaymentStatus', 'paymentStatus', 'status', 'Status'
        ]
        val = None
        for k in candidates:
            if isinstance(payload.get(k), str) and payload.get(k).strip():
                val = payload.get(k).strip()
                break
        if not val and isinstance(payload.get('result'), dict):
            # Sometimes nested under 'result'
            res = payload['result']
            for k in candidates:
                if isinstance(res.get(k), str) and res.get(k).strip():
                    val = res.get(k).strip()
                    break
        return val.upper() if isinstance(val, str) else None
    except Exception:
        return None


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
    response = requests.get(url, headers=headers, params=params, timeout=30)
    try:
        js = response.json()
    except Exception:
        js = {}
    if response.status_code == 200:
        return _parse_payment_status(js)
    else:
        return None


def get_transaction_status_details(access_token, tracking_id=None, merchant_reference=None):
    """Return a dict with normalized details about a transaction status.
    Keys: status, phone_number, payment_method, tracking_id, raw
    """
    url = f"{BASE_URL}/api/Transactions/GetTransactionStatus"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {}
    if tracking_id:
        params["order_tracking_id"] = tracking_id
    if merchant_reference:
        params["order_merchant_reference"] = merchant_reference
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    try:
        js = resp.json()
    except Exception:
        js = {}

    status = _parse_payment_status(js)

    # Normalize potential phone keys
    phone = None
    phone_keys = [
        'phone_number', 'PhoneNumber', 'consumer_phone_number', 'msisdn', 'MSISDN', 'account_number', 'AccountNumber'
    ]
    for k in phone_keys:
        val = js.get(k)
        if isinstance(val, str) and val.strip():
            phone = val.strip()
            break
    # Normalize method keys
    method = None
    method_keys = ['payment_method', 'PaymentMethod', 'paymentMethod', 'channel', 'Channel']
    for k in method_keys:
        val = js.get(k)
        if isinstance(val, str) and val.strip():
            method = val.strip()
            break
    # Tracking id in payload if present
    track = None
    track_keys = ['order_tracking_id', 'OrderTrackingId', 'tracking_id', 'TrackingId']
    for k in track_keys:
        val = js.get(k)
        if isinstance(val, str) and val.strip():
            track = val.strip()
            break

    return {
        'status': status,
        'phone_number': phone,
        'payment_method': method,
        'tracking_id': track or tracking_id,
        'raw': js,
        'http_status': resp.status_code,
    }


