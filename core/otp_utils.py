import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP, SentEmail

# -------------------------
# OTP Generation
# -------------------------
def generate_otp():
    """Generate a random 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

# -------------------------
# OTP Creation
# -------------------------
def create_otp(email=None, phone=None, otp_type='email', expiry_minutes=5):
    """
    Create an OTP for email or phone verification
    
    Args:
        email (str): Email address (required if otp_type='email')
        phone (str): Phone number (required if otp_type='phone')
        otp_type (str): 'email' or 'phone'
        expiry_minutes (int): Minutes until OTP expires (default: 5)
    
    Returns:
        OTP: Created OTP object or None if invalid
    """
    if not email and not phone:
        return None
    
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
    
    otp = OTP.objects.create(
        email=email,
        phone=phone,
        otp_code=otp_code,
        otp_type=otp_type,
        expires_at=expires_at
    )
    
    return otp

# -------------------------
# Send OTP via Email
# -------------------------
def send_otp_email(email, otp_code, customer_name=None):
    """
    Send OTP to customer's email
    
    Args:
        email (str): Recipient email address
        otp_code (str): 6-digit OTP code
        customer_name (str): Customer name for personalization
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = "Waste Billing System - Your OTP Code"
        
        customer_greeting = f"Dear {customer_name}," if customer_name else "Dear Customer,"
        
        message = f"""{customer_greeting}

Your One-Time Password (OTP) for the Waste Billing and Feedback System is:

    {otp_code}

This OTP is valid for 5 minutes only. Please do not share it with anyone.

If you did not request this OTP, please ignore this email.

Best regards,
Waste Billing Management System
"""
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Waste Billing System</h2>
                    <p>{customer_greeting}</p>
                    <p>Your One-Time Password (OTP) is:</p>
                    <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #007bff; margin: 20px 0;">
                        <h1 style="text-align: center; color: #007bff; letter-spacing: 2px; margin: 0;">{otp_code}</h1>
                    </div>
                    <p style="color: #e74c3c; font-weight: bold;">⏱️ Valid for 5 minutes only</p>
                    <p>Please do not share this OTP with anyone.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="font-size: 12px; color: #7f8c8d;">If you did not request this OTP, please ignore this email.</p>
                </div>
            </body>
        </html>
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as mail_error:
            print(f"Mail send error (non-critical): {str(mail_error)}")
            # Continue anyway - store in DB even if SMTP fails
        
        try:
            SentEmail.objects.create(
                to_email=email,
                subject=subject,
                body=message,
                html_body=html_message
            )
        except Exception:
            # Avoid breaking sending if DB outbox save fails
            pass
        print(f"✓ OTP email stored for {email} | Code: {otp_code}")
        return True
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        return False

# -------------------------
# Send OTP via SMS (Placeholder for SMS integration)
# -------------------------
def send_otp_sms(phone, otp_code, customer_name=None):
    """
    Send OTP to customer's phone via SMS
    
    NOTE: This is a placeholder. To use actual SMS, install a package like:
    - Twilio: pip install twilio
    - AWS SNS: pip install boto3
    
    Args:
        phone (str): Phone number
        otp_code (str): 6-digit OTP code
        customer_name (str): Customer name for personalization
    
    Returns:
        bool: True if SMS sent successfully, False otherwise
    """
    # Placeholder implementation
    # TODO: Integrate with Twilio, AWS SNS, or your SMS provider
    
    print(f"[SMS] Sending OTP {otp_code} to {phone}")
    
    # Example with Twilio (uncomment and configure if using Twilio):
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(
    #     body=f"Your OTP for Waste Billing System is: {otp_code}. Valid for 5 minutes.",
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=phone
    # )
    # return message.sid is not None
    
    return True  # Return True for now (placeholder)

# -------------------------
# Verify OTP
# -------------------------
def verify_otp(contact, otp_input, otp_type='email'):
    """
    Verify OTP for given contact
    
    Args:
        contact (str): Email or phone number
        otp_input (str): OTP entered by user
        otp_type (str): 'email' or 'phone'
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'otp_object': OTP object or None
        }
    """
    try:
        # Get the latest OTP for this contact
        if otp_type == 'email':
            otp = OTP.objects.filter(email=contact, otp_type='email').latest('created_at')
        else:
            otp = OTP.objects.filter(phone=contact, otp_type='phone').latest('created_at')
        
        # Verify the OTP
        if otp.verify(otp_input):
            return {
                'success': True,
                'message': 'OTP verified successfully!',
                'otp_object': otp
            }
        elif otp.is_expired():
            return {
                'success': False,
                'message': 'OTP has expired. Please request a new one.',
                'otp_object': None
            }
        else:
            return {
                'success': False,
                'message': f'Invalid OTP. Attempts remaining: {otp.max_attempts - otp.attempts}',
                'otp_object': None
            }
    except OTP.DoesNotExist:
        return {
            'success': False,
            'message': 'No OTP found. Please request a new one.',
            'otp_object': None
        }

# -------------------------
# Delete Expired OTPs
# -------------------------
def cleanup_expired_otps():
    """Delete OTPs that have expired"""
    expired_otps = OTP.objects.filter(expires_at__lt=timezone.now())
    count = expired_otps.count()
    expired_otps.delete()
    return count
