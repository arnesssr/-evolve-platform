from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import requests
from django.conf import settings

def send_otp(email, phone, code):
    # Send Email (fail-safe)
    subject = "Your OTP Code"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', "info@lixnet.net")
    to = [email]

    # Plain text version (fallback)
    text_content = f"Use the following OTP to complete your login: {code}"

    # HTML version
    html_content = render_to_string('emails/otp_email.html', {'code': code})

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        # Do not crash if SMTP is not configured
        msg.send(fail_silently=True)
        print(f"✅ OTP email queued/sent to {email}")
    except Exception as e:
        # Never let email failures break registration
        print(f"❌ Failed to send OTP email to {email}: {e}")

    message = f"Use the following OTP to complete your login: {code}"

    # Send SMS (fail-safe)
    try:
        if phone:
            send_sms(phone, message)
    except Exception as e:
        print(f"❌ Failed to send OTP SMS to {phone}: {e}")


def send_mail(email, code):
    """
    Send email-only OTP (fallback when phone number is not available)
    """
    subject = "Your OTP Code"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', "info@lixnet.net")
    to = [email]

    # Plain text version (fallback)
    text_content = f"Use the following OTP to complete your login: {code}"

    # HTML version
    html_content = render_to_string('emails/otp_email.html', {'code': code})

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
        print("✅ Email-only OTP queued/sent to:", email)
    except Exception as e:
        print(f"❌ Failed to send email-only OTP to {email}: {e}")


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
