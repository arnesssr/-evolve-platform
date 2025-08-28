from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import requests
from django.conf import settings

def send_otp(email, phone, code):
    # Send Email (fail-safe)
    subject = "Your OTP Code"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', "evolve@lixnet.net")
    to = [email]

    # Plain text version (fallback)
    text_content = f"Use the following OTP to complete your login: {code}"

    # HTML version
    html_content = render_to_string('emails/otp_email.html', {'code': code})

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        # Send email - will not crash even if there's an error
        msg.send(fail_silently=False)
        print(f"✅ OTP email sent to {email}")
    except Exception as e:
        # Log the error but don't break the flow
        print(f"❌ Failed to send OTP email to {email}: {e}")
        # Try sending plain text email as fallback
        try:
            from django.core.mail import send_mail as django_send_mail
            django_send_mail(subject, text_content, from_email, to, fail_silently=False)
            print(f"✅ Plain text OTP email sent to {email}")
        except Exception as fallback_error:
            print(f"❌ Fallback email also failed: {fallback_error}")

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
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', "evolve@lixnet.net")
    to = [email]

    # Plain text version (fallback)
    text_content = f"Use the following OTP to complete your login: {code}"

    # HTML version
    html_content = render_to_string('emails/otp_email.html', {'code': code})

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        print(f"✅ Email-only OTP sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send email-only OTP to {email}: {e}")
        # Try sending plain text email as fallback
        try:
            from django.core.mail import send_mail as django_send_mail
            django_send_mail(subject, text_content, from_email, to, fail_silently=False)
            print(f"✅ Plain text OTP email sent to {email}")
        except Exception as fallback_error:
            print(f"❌ Fallback email also failed: {fallback_error}")


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
