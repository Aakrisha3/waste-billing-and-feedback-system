# OTP Integration Guide

## Overview
This document explains how to integrate and use the One-Time Password (OTP) authentication system in your Waste Billing and Feedback System.

## What's Included

### 1. **New Database Model** (`OTP`)
- Email/Phone based OTP storage
- Automatic expiration handling
- Verification attempt tracking
- Fields:
  - `email`: Customer email (optional)
  - `phone`: Customer phone (optional)
  - `otp_code`: 6-digit OTP
  - `otp_type`: 'email' or 'phone'
  - `is_verified`: Verification status
  - `expires_at`: Expiration timestamp
  - `attempts`: Failed attempt counter
  - `max_attempts`: Maximum allowed attempts (default: 5)

### 2. **OTP Utilities** (`otp_utils.py`)
Helper functions for OTP operations:
- `generate_otp()`: Generate random 6-digit OTP
- `create_otp()`: Create OTP record in database
- `send_otp_email()`: Send OTP via email
- `send_otp_sms()`: Send OTP via SMS (placeholder)
- `verify_otp()`: Verify user-entered OTP
- `cleanup_expired_otps()`: Delete expired OTPs

### 3. **Views** (Added to `views.py`)
- `request_otp()`: Request OTP via email or phone
- `verify_otp_view()`: Verify the OTP entered by user
- `resend_otp()`: Resend OTP if user didn't receive it
- `customer_logout()`: Logout authenticated customer

### 4. **Forms** (Added to `forms.py`)
- `RequestOTPForm`: Validate and request OTP
- `VerifyOTPForm`: Validate OTP input
- `OTPModelForm`: Admin form for OTP management

### 5. **Templates**
- `request_otp.html`: Request OTP page
- `verify_otp.html`: Verify OTP page

## Installation Steps

### Step 1: Create Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Configure Email Settings
Edit `waste_billing/settings.py` and choose your email configuration:

#### Option A: Development (Console Backend - Emails print to console)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@wastebilling.local'
```

#### Option B: Gmail
1. Enable 2-factor authentication on your Gmail account
2. Create an App Password: https://myaccount.google.com/apppasswords
3. Update settings:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # From step 2
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

#### Option C: Other SMTP Providers
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-host'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-username'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

### Step 3: (Optional) Configure SMS Integration
For SMS support, install Twilio:
```bash
pip install twilio
```

Update `waste_billing/settings.py`:
```python
TWILIO_ACCOUNT_SID = 'your-account-sid'
TWILIO_AUTH_TOKEN = 'your-auth-token'
TWILIO_PHONE_NUMBER = '+1234567890'
```

Then uncomment the Twilio code in `otp_utils.py`:
```python
def send_otp_sms(phone, otp_code, customer_name=None):
    from twilio.rest import Client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your OTP for Waste Billing System is: {otp_code}. Valid for 5 minutes.",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone
    )
    return message.sid is not None
```

## Usage

### For Customers (OTP Login)

1. **Request OTP**
   - Navigate to `/otp/request/`
   - Select email or phone
   - Enter registered contact information
   - Click "Request OTP"

2. **Verify OTP**
   - Enter the 6-digit code received
   - Click "Verify & Login"
   - On success, redirected to customer dashboard

3. **Resend OTP**
   - Click "Resend OTP" if code not received
   - New OTP will be sent (old one expires)

4. **Logout**
   - Click logout to clear customer session

### For Developers (Using OTP Functions)

```python
from core.otp_utils import create_otp, send_otp_email, verify_otp

# Create OTP for email
otp = create_otp(
    email='customer@example.com',
    otp_type='email',
    expiry_minutes=5
)

# Send OTP via email
send_otp_email('customer@example.com', otp.otp_code, 'John Doe')

# Verify OTP
result = verify_otp('customer@example.com', '123456', 'email')
if result['success']:
    print("OTP verified!")
else:
    print(result['message'])
```

## URL Routes

```
GET/POST  /otp/request/       - Request OTP
GET/POST  /otp/verify/        - Verify OTP
GET       /otp/resend/        - Resend OTP
GET       /otp/logout/        - Customer logout
```

## Security Features

1. **OTP Expiration**: OTPs expire after 5 minutes (configurable)
2. **Attempt Limiting**: Maximum 5 failed attempts (configurable)
3. **Unique Code**: 6-digit random numbers for each request
4. **Session Based**: Session data cleared after verification
5. **CSRF Protection**: All forms protected with CSRF tokens

## Configuration Options

Edit `waste_billing/settings.py`:

```python
# OTP validity duration (minutes)
OTP_EXPIRY_MINUTES = 5

# Maximum verification attempts
OTP_MAX_ATTEMPTS = 5
```

## Admin Interface

Register OTP model in admin for management:

Add to `core/admin.py`:
```python
from django.contrib import admin
from .models import OTP

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'otp_type', 'is_verified', 'created_at']
    list_filter = ['otp_type', 'is_verified', 'created_at']
    search_fields = ['email', 'phone']
    readonly_fields = ['otp_code', 'created_at', 'expires_at']
```

## Troubleshooting

### Emails not sending in development
- Check Django console output for email content
- Make sure `EMAIL_BACKEND` is set to `console.EmailBackend`

### Emails not sending in production
- Verify SMTP credentials are correct
- Check if firewall blocks port 587
- Test SMTP connection manually
- Check email logs in Django

### SMS not sending
- Ensure Twilio account is active and funded
- Verify phone number format (E.164: +1234567890)
- Check Twilio logs in dashboard

### OTP verification failing
- Ensure OTP hasn't expired (5 minutes)
- Check max attempts not exceeded (5 attempts)
- Verify OTP code matches exactly (case-sensitive)

## Cleanup (Optional)

To remove old/expired OTPs from database:

```python
from core.otp_utils import cleanup_expired_otps

# Delete expired OTPs
cleanup_expired_otps()

# Or run as management command:
# python manage.py cleanup_otps
```

## Best Practices

1. **Use HTTPS in Production**: Protect OTP transmission
2. **Secure Email/SMS**: Don't log sensitive OTP codes
3. **Rate Limiting**: Consider implementing rate limiting for OTP requests
4. **Monitoring**: Track failed OTP attempts for security
5. **Backup**: Keep email/phone verification options
6. **User Education**: Inform users never to share OTPs

## Common Modifications

### Change OTP Length
In `otp_utils.py`:
```python
def generate_otp():
    return ''.join(random.choices(string.digits, k=8))  # 8 digits instead of 6
```

### Custom OTP Message
In `otp_utils.py` modify `send_otp_email()` function

### Add WhatsApp Support
Install `twilio-python` and use WhatsApp API in `send_otp_sms()`

## Support

For issues or questions:
1. Check Django error logs
2. Verify database migrations ran successfully
3. Test email configuration separately
4. Check customer exists in database with correct contact info
