from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import requests
from django.conf import settings

def send_otp(email, phone, code):
    # Send Email
    subject = "Your OTP Code"
    from_email = "info@lixnet.net"
    to = [email]
    
    # Plain text version (fallback)
    text_content = f"Use the following OTP to complete your login: {code}"

    # HTML version
    html_content = render_to_string('emails/otp_email.html', {'code': code})

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    message = f"Use the following OTP to complete your login: {code}"

    # Send SMS
    send_sms(phone, message)


def send_mail(email, code):
    """
    Send email-only OTP (fallback when phone number is not available)
    """
    subject = "Your OTP Code"
    from_email = "info@lixnet.net"
    to = [email]
    
    # Plain text version (fallback)
    text_content = f"Use the following OTP to complete your login: {code}"

    # HTML version
    html_content = render_to_string('emails/otp_email.html', {'code': code})

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print("✅ Email-only OTP sent to:", email)


def send_sms(phone_number, message):
    base_url = "https://api.smsleopard.com/v1/sms/send"

    params = {
        "username": settings.SMSLEOPARD_API_KEY,
        "password": settings.SMSLEOPARD_API_SECRET,
        "message": message,
        "destination": phone_number
        # Note: Removed source parameter due to sender ID restrictions
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        print("✅ SMS sent:", response.text)
        return response.text
    except requests.HTTPError as e:
        print("❌ HTTP Error:", e.response.status_code, e.response.text)
    except requests.RequestException as e:
        print("❌ Request failed:", e)
