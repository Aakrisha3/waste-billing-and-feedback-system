# OTP Integration - Code Examples

## Email Configuration Examples

### Example 1: Development (Console Backend)
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@wastebilling.local'

# Output: OTP emails print to console
# Perfect for development and testing
```

### Example 2: Gmail with App Password
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mycompany@gmail.com'
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # 16-char App Password
DEFAULT_FROM_EMAIL = 'mycompany@gmail.com'
```

### Example 3: Office 365
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'company@office365.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'company@office365.com'
```

## Using OTP in Your Code

### Example 1: Request OTP for a Customer
```python
from core.models import Customer
from core.otp_utils import create_otp, send_otp_email

# Get customer
customer = Customer.objects.get(email='john@example.com')

# Create OTP
otp = create_otp(
    email=customer.email,
    otp_type='email',
    expiry_minutes=5
)

# Send via email
send_otp_email(
    email=customer.email,
    otp_code=otp.otp_code,
    customer_name=customer.name
)
```

### Example 2: Verify OTP Entry
```python
from core.otp_utils import verify_otp

# User enters OTP
user_input = '123456'

# Verify it
result = verify_otp(
    contact='john@example.com',
    otp_input=user_input,
    otp_type='email'
)

if result['success']:
    print(f"✓ OTP verified! {result['message']}")
else:
    print(f"✗ Verification failed: {result['message']}")
```

### Example 3: Add OTP to Custom View
```python
from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import Customer
from core.otp_utils import create_otp, send_otp_email

def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Find customer
        customer = Customer.objects.filter(email=email).first()
        if not customer:
            messages.error(request, 'Customer not found')
            return render(request, 'custom_login.html')
        
        # Create and send OTP
        otp = create_otp(email=email, otp_type='email')
        send_otp_email(email, otp.otp_code, customer.name)
        
        messages.success(request, f'OTP sent to {email}')
        request.session['customer_email'] = email
        return redirect('verify_otp')
    
    return render(request, 'custom_login.html')
```

### Example 4: SMS Integration with Twilio
```python
# settings.py - Add Twilio config
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+12025551234'

# otp_utils.py - Update send_otp_sms function
from twilio.rest import Client
from django.conf import settings

def send_otp_sms(phone, otp_code, customer_name=None):
    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        message_body = f"Your OTP for Waste Billing is: {otp_code}. Valid for 5 minutes only."
        
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        
        return message.sid is not None
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False
```

## Admin Interface Setup

### Register OTP in Admin
```python
# core/admin.py
from django.contrib import admin
from .models import OTP

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['contact_info', 'otp_type', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['otp_type', 'is_verified', 'created_at']
    search_fields = ['email', 'phone']
    readonly_fields = ['otp_code', 'created_at', 'expires_at']
    
    def contact_info(self, obj):
        if obj.email:
            return f"📧 {obj.email}"
        return f"📱 {obj.phone}"
    contact_info.short_description = "Contact"
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Edit mode
            return self.readonly_fields + ['email', 'phone', 'otp_type']
        return self.readonly_fields
```

## OTP Management Commands

### Create Management Command for Cleanup
```python
# core/management/commands/cleanup_otps.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import OTP

class Command(BaseCommand):
    help = 'Delete expired OTPs'
    
    def handle(self, *args, **options):
        deleted_count = OTP.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_count} expired OTPs'
            )
        )
```

Run with:
```bash
python manage.py cleanup_otps
```

## Template Customization

### Custom OTP Email Template
```python
# otp_utils.py - Create HTML template

HTML_EMAIL_TEMPLATE = """
<html>
<body style="font-family: Arial; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 20px auto; background: white; padding: 20px; border-radius: 8px;">
        <h2 style="color: #333;">Waste Billing System</h2>
        <p>Hi {customer_name},</p>
        <p>Your One-Time Password is:</p>
        <div style="text-align: center; margin: 30px 0;">
            <span style="font-size: 36px; font-weight: bold; color: #007bff; letter-spacing: 5px;">
                {otp_code}
            </span>
        </div>
        <p style="color: #666;">This code expires in 5 minutes.</p>
        <hr>
        <p style="font-size: 12px; color: #999;">
            © 2024 Waste Billing Management System. All rights reserved.
        </p>
    </div>
</body>
</html>
"""
```

## Testing OTP Functionality

### Unit Test Example
```python
# core/tests.py
from django.test import TestCase
from core.models import Customer, OTP
from core.otp_utils import create_otp, verify_otp

class OTPTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test User',
            email='test@example.com',
            phone='9876543210'
        )
    
    def test_create_otp(self):
        """Test OTP creation"""
        otp = create_otp(
            email=self.customer.email,
            otp_type='email'
        )
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.otp_code), 6)
        self.assertTrue(otp.otp_code.isdigit())
    
    def test_verify_otp_success(self):
        """Test successful OTP verification"""
        otp = create_otp(
            email=self.customer.email,
            otp_type='email'
        )
        
        result = verify_otp(
            contact=self.customer.email,
            otp_input=otp.otp_code,
            otp_type='email'
        )
        
        self.assertTrue(result['success'])
    
    def test_verify_otp_invalid(self):
        """Test invalid OTP verification"""
        create_otp(email=self.customer.email, otp_type='email')
        
        result = verify_otp(
            contact=self.customer.email,
            otp_input='000000',
            otp_type='email'
        )
        
        self.assertFalse(result['success'])
```

Run tests:
```bash
python manage.py test core.tests.OTPTestCase
```

## Error Handling

### Custom Exception Handling
```python
from django.core.mail import EmailError

try:
    send_otp_email(customer.email, otp.otp_code)
except EmailError as e:
    messages.error(request, f'Failed to send OTP: {str(e)}')
    return redirect('request_otp')
```

### Logging OTP Attempts
```python
import logging

logger = logging.getLogger(__name__)

def verify_otp_with_logging(contact, otp_input, otp_type):
    result = verify_otp(contact, otp_input, otp_type)
    
    if result['success']:
        logger.info(f"OTP verified for {otp_type}: {contact}")
    else:
        logger.warning(f"Failed OTP verification for {otp_type}: {contact}")
    
    return result
```

## Security Enhancements

### Rate Limiting (using Django Cache)
```python
from django.core.cache import cache
from django.http import HttpResponse

def rate_limited_otp_request(request):
    email = request.POST.get('email')
    cache_key = f'otp_request_{email}'
    
    # Check if already requested in last minute
    if cache.get(cache_key):
        messages.error(request, 'Please wait 1 minute before requesting another OTP')
        return redirect('request_otp')
    
    # Set cache for 1 minute
    cache.set(cache_key, True, 60)
    
    # Proceed with OTP creation
    otp = create_otp(email=email, otp_type='email')
    send_otp_email(email, otp.otp_code)
    return redirect('verify_otp')
```

### Hash OTP for Storage (Optional)
```python
from django.contrib.auth.hashers import make_password, check_password

# When creating OTP
otp_code = generate_otp()
hashed_otp = make_password(otp_code)

# When verifying
if check_password(user_input, hashed_otp):
    # OTP is valid
    pass
```

---

**Need more examples?** Check the main OTP_INTEGRATION_GUIDE.md file.
