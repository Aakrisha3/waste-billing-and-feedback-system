# OTP Integration - Implementation Reference

## File-by-File Changes

### 1. core/models.py
**Added OTP Model**
```python
class OTP(models.Model):
    OTP_TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]
    
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.is_expired() and not self.is_verified and self.attempts < self.max_attempts
    
    def verify(self, otp_input):
        if not self.is_valid():
            return False
        if self.otp_code == otp_input:
            self.is_verified = True
            self.save()
            return True
        self.attempts += 1
        self.save()
        return False
```

### 2. core/otp_utils.py
**New File - OTP Utilities**
- `generate_otp()` - Generate 6-digit code
- `create_otp()` - Create OTP record
- `send_otp_email()` - Send via email
- `send_otp_sms()` - Send via SMS
- `verify_otp()` - Verify code
- `cleanup_expired_otps()` - Delete expired

### 3. core/views.py
**Added 4 OTP Views**
```python
def request_otp(request):
    # Request OTP via email or phone
    
def verify_otp_view(request):
    # Verify the OTP code
    
def resend_otp(request):
    # Resend OTP to customer
    
def customer_logout(request):
    # Logout authenticated customer
```

### 4. core/forms.py
**Added 3 OTP Forms**
```python
class RequestOTPForm(forms.Form):
    # Validate email/phone input
    
class VerifyOTPForm(forms.Form):
    # Validate 6-digit OTP
    
class OTPModelForm(forms.ModelForm):
    # Admin form for OTP
```

### 5. core/urls.py
**Added 4 Routes**
```python
path('otp/request/', views.request_otp, name='request_otp')
path('otp/verify/', views.verify_otp_view, name='verify_otp')
path('otp/resend/', views.resend_otp, name='resend_otp')
path('otp/logout/', views.customer_logout, name='customer_logout')
```

### 6. core/templates/core/request_otp.html
**New Template**
- Radio buttons for email/phone selection
- Dynamic placeholder updates
- Professional card design
- Responsive layout

### 7. core/templates/core/verify_otp.html
**New Template**
- OTP input field (6 digits)
- Resend and change contact buttons
- Countdown timer ready
- Mobile-optimized

### 8. waste_billing/settings.py
**Added Configuration**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@wastebilling.local'

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 5
```

## Integration Checklist

### Before First Run
- [ ] Run migrations: `python manage.py makemigrations && python manage.py migrate`
- [ ] Configure EMAIL_BACKEND in settings.py
- [ ] Test email configuration
- [ ] Create test customer with email/phone

### For Production
- [ ] Use proper email provider (Gmail, SendGrid, etc.)
- [ ] Set DEBUG = False
- [ ] Use HTTPS
- [ ] Add rate limiting
- [ ] Monitor OTP attempts
- [ ] Set up error logging

## API Reference

### OTP Model
```python
from core.models import OTP

# Create OTP
otp = OTP.objects.create(
    email='user@example.com',
    otp_code='123456',
    otp_type='email',
    expires_at=expires_at
)

# Check if valid
if otp.is_valid():
    print("OTP can be verified")

# Verify OTP
if otp.verify('123456'):
    print("OTP verified!")
```

### OTP Utils
```python
from core.otp_utils import *

# Generate OTP
code = generate_otp()  # Returns '123456'

# Create OTP
otp = create_otp(
    email='user@example.com',
    otp_type='email',
    expiry_minutes=5
)

# Send email
success = send_otp_email(
    email='user@example.com',
    otp_code='123456',
    customer_name='John'
)

# Send SMS (placeholder)
success = send_otp_sms(
    phone='+12025551234',
    otp_code='123456',
    customer_name='John'
)

# Verify
result = verify_otp(
    contact='user@example.com',
    otp_input='123456',
    otp_type='email'
)

# Cleanup
count = cleanup_expired_otps()
```

## Email Configuration Samples

### Console (Development)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Gmail SMTP
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'app-password-from-google'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

### SendGrid SMTP
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'SG.xxxxxxxxxxxxx'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

## URL Routes Reference

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET/POST | `/otp/request/` | `request_otp` | Request OTP |
| GET/POST | `/otp/verify/` | `verify_otp_view` | Verify OTP |
| GET | `/otp/resend/` | `resend_otp` | Resend OTP |
| GET | `/otp/logout/` | `customer_logout` | Logout |

## Database Operations

### View All OTPs
```python
from core.models import OTP

otps = OTP.objects.all()

# Filter by email
otps = OTP.objects.filter(email='user@example.com')

# Filter by phone
otps = OTP.objects.filter(phone='9876543210')

# Filter by type
otps = OTP.objects.filter(otp_type='email')

# Filter verified
verified = OTP.objects.filter(is_verified=True)

# Get latest for contact
latest = OTP.objects.filter(
    email='user@example.com'
).latest('created_at')
```

### Delete OTPs
```python
# Delete specific OTP
otp = OTP.objects.get(id=1)
otp.delete()

# Delete expired
from django.utils import timezone
OTP.objects.filter(expires_at__lt=timezone.now()).delete()

# Delete unverified after 1 hour
from datetime import timedelta
cutoff = timezone.now() - timedelta(hours=1)
OTP.objects.filter(
    is_verified=False,
    created_at__lt=cutoff
).delete()
```

## Session Data

### What Gets Stored in Session
```python
request.session['contact_type']   # 'email' or 'phone'
request.session['contact_value']  # 'user@example.com' or '9876543210'
request.session['customer_id']    # Customer ID
request.session['authenticated']  # True after verification
```

### Clear Session
```python
# Clear specific keys
del request.session['contact_type']
del request.session['contact_value']

# Clear all
request.session.flush()
```

## Error Messages

### System Messages
- "Please provide contact information."
- "No customer found with this contact information."
- "OTP sent successfully."
- "Failed to send OTP. Please try again."
- "Please enter a valid 6-digit OTP."
- "OTP has expired. Please request a new one."
- "Invalid OTP. Attempts remaining: X"
- "Session expired. Please request OTP again."

## Performance Considerations

### Optimization Tips
1. Index OTP table on email, phone, created_at
2. Clean up expired OTPs regularly (daily cron job)
3. Use cache for rate limiting
4. Consider OTP table partitioning for large scale

### Database Indexes
```python
# In models.py OTP class
class Meta:
    indexes = [
        models.Index(fields=['email']),
        models.Index(fields=['phone']),
        models.Index(fields=['created_at']),
        models.Index(fields=['is_verified']),
    ]
```

## Security Best Practices

1. ✅ Use HTTPS in production
2. ✅ Don't log OTP codes
3. ✅ Implement rate limiting
4. ✅ Monitor failed attempts
5. ✅ Hash OTP in database (optional)
6. ✅ Add CAPTCHA to prevent brute force
7. ✅ Notify user of OTP sent
8. ✅ Delete OTPs after verification

## Common Modifications

### Add Custom Email Template
Edit `send_otp_email()` in `otp_utils.py`

### Change OTP Length
```python
def generate_otp():
    return ''.join(random.choices(string.digits, k=8))
```

### Add Custom Validation
```python
def clean_contact_value(self):
    # Add custom validation logic
    pass
```

### Add OTP History
```python
class OTPHistory(models.Model):
    otp = models.ForeignKey(OTP, on_delete=models.CASCADE)
    verified_at = models.DateTimeField(auto_now_add=True)
    user_ip = models.GenericIPAddressField()
```

## Testing Utilities

### Test Email Configuration
```bash
python manage.py shell
from django.core.mail import send_mail
send_mail(
    'Test',
    'This is a test',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### Test OTP Flow
```bash
python manage.py shell
from core.otp_utils import create_otp, verify_otp
from core.models import Customer

# Create test customer
customer = Customer.objects.first()

# Create OTP
otp = create_otp(email=customer.email, otp_type='email')

# Verify with correct code
result = verify_otp(customer.email, otp.otp_code, 'email')
print(result)  # Should be success

# Verify with wrong code
result = verify_otp(customer.email, '000000', 'email')
print(result)  # Should be failure
```

---

**For more information, refer to:**
- OTP_INTEGRATION_GUIDE.md - Complete guide
- OTP_SETUP_CHECKLIST.md - Setup steps
- OTP_CODE_EXAMPLES.md - Code examples
