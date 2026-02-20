# OTP Integration - Quick Reference Guide

## 🚀 30-Second Setup

```bash
# 1. Run migrations
python manage.py makemigrations
python manage.py migrate

# 2. Set email (already configured for console)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 3. Test
python manage.py runserver
# Visit: http://localhost:8000/otp/request/
```

## 📋 Feature Checklist

- ✅ Email OTP support
- ✅ Phone OTP support (SMS ready)
- ✅ 6-digit random generation
- ✅ 5-minute expiration
- ✅ 5 attempt limit
- ✅ Session-based authentication
- ✅ Resend functionality
- ✅ Professional UI
- ✅ Mobile responsive
- ✅ Error handling
- ✅ CSRF protection
- ✅ Rate limiting ready

## 🔗 URL Routes

```
/otp/request/   ← Request OTP (email/phone)
/otp/verify/    ← Verify OTP code
/otp/resend/    ← Resend OTP
/otp/logout/    ← Logout customer
```

## 📝 Models & Functions

### Model: OTP
```python
OTP(
    email, phone,              # Contact info
    otp_code,                  # 6-digit code
    otp_type,                  # 'email' or 'phone'
    is_verified,               # Verification status
    created_at, expires_at,    # Timestamps
    attempts, max_attempts     # Attempt tracking
)
```

### Key Functions
```python
generate_otp()              → '123456'
create_otp()                → OTP object
send_otp_email()            → True/False
send_otp_sms()              → True/False
verify_otp()                → {'success': bool, 'message': str}
cleanup_expired_otps()      → count
```

## 🔧 Configuration

### Email - Pick One

**Development**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Gmail**
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your@gmail.com'
EMAIL_HOST_PASSWORD = 'app-password'
```

**SendGrid**
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'SG.xxxxx'
```

### OTP Settings
```python
OTP_EXPIRY_MINUTES = 5      # Change validity
OTP_MAX_ATTEMPTS = 5        # Change attempt limit
```

## 🧪 Quick Test

```bash
python manage.py shell

# 1. Create test customer
from core.models import Customer
c = Customer.objects.create(name='Test', email='test@example.com', phone='9876543210')

# 2. Create OTP
from core.otp_utils import create_otp, send_otp_email
otp = create_otp(email='test@example.com', otp_type='email')

# 3. Send email
send_otp_email('test@example.com', otp.otp_code, 'Test')

# 4. Verify
from core.otp_utils import verify_otp
result = verify_otp('test@example.com', otp.otp_code, 'email')
print(result)  # {'success': True, ...}
```

## 📧 Email Providers Setup

| Provider | Host | Port | Username | Password |
|----------|------|------|----------|----------|
| Gmail | smtp.gmail.com | 587 | email@gmail.com | App Password |
| Office365 | smtp.office365.com | 587 | email@office.com | Password |
| SendGrid | smtp.sendgrid.net | 587 | apikey | API Key |
| AWS SES | email.region.amazonaws.com | 587 | AWS User | AWS Password |

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No emails | Check EMAIL_BACKEND setting |
| Migration error | Run `python manage.py makemigrations core` |
| Customer not found | Check email/phone in Customer table |
| OTP expired | Wait less than 5 minutes |
| Too many attempts | Wait for new OTP |

## 📱 SMS Integration

```bash
# 1. Install Twilio
pip install twilio

# 2. Add settings
TWILIO_ACCOUNT_SID = 'ACxxxxxxx'
TWILIO_AUTH_TOKEN = 'xxxxxxx'
TWILIO_PHONE_NUMBER = '+1234567890'

# 3. Uncomment SMS code in otp_utils.py
# Done! SMS now works
```

## 🔐 Security Checklist

- [ ] Use HTTPS in production
- [ ] Don't log OTP codes
- [ ] Keep email credentials secure
- [ ] Use App Passwords (not main password)
- [ ] Enable 2FA on email account
- [ ] Monitor failed attempts
- [ ] Delete old OTPs regularly
- [ ] Add rate limiting

## 📞 Support Links

- Django Email: https://docs.djangoproject.com/en/stable/topics/email/
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- Twilio: https://www.twilio.com/docs/sms
- SendGrid: https://sendgrid.com/docs/

## 💡 Tips & Tricks

**Auto-submit OTP form** (verify_otp.html)
```javascript
if (this.value.length === 6) {
    this.form.submit();
}
```

**Add countdown timer** (verify_otp.html)
```html
<p>OTP expires in <span id="timer">5:00</span></p>
<script>
    let seconds = 300;
    setInterval(() => {
        let mins = Math.floor(seconds / 60);
        let secs = seconds % 60;
        document.getElementById('timer').textContent = 
            `${mins}:${secs.toString().padStart(2, '0')}`;
        seconds--;
    }, 1000);
</script>
```

**Custom OTP length**
```python
# In otp_utils.py
def generate_otp():
    return ''.join(random.choices(string.digits, k=8))  # 8 digits
```

**Hash OTP in database** (optional)
```python
from django.contrib.auth.hashers import make_password
otp_code = make_password('123456')
```

## 🎯 Common Customizations

**Change expiry to 10 minutes**
```python
create_otp(..., expiry_minutes=10)
```

**Change max attempts to 3**
```python
OTP.max_attempts = 3
```

**Send HTML email**
```python
# Already implemented in send_otp_email()
```

**Add customer name in SMS**
```python
f"Hi {customer_name}, your OTP is: {otp_code}"
```

## 📊 OTP Status Codes

| Status | Meaning | Next Step |
|--------|---------|-----------|
| ✓ | OTP verified | Login successful |
| ✗ | Wrong code | Retry |
| ⏰ | Expired | Request new |
| 🚫 | Max attempts | Request new |
| ❌ | Not found | Request OTP |

## 🔄 Flow Diagram

```
Start
  ↓
Choose email/phone
  ↓
Enter contact info
  ↓
Generate 6-digit OTP
  ↓
Send via email/SMS
  ↓
Show verify page
  ↓
User enters OTP
  ↓
Verify match?
  → No: Show error, attempts--
  → Yes: Check expiry?
    → Expired: Error, request new
    → Valid: Login successful ✓
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `core/models.py` | OTP model definition |
| `core/otp_utils.py` | OTP functions |
| `core/views.py` | OTP view handlers |
| `core/forms.py` | OTP validation forms |
| `core/urls.py` | OTP URL routes |
| `request_otp.html` | Request page |
| `verify_otp.html` | Verify page |

## 🎓 Learning Resources

1. **Start**: OTP_SETUP_CHECKLIST.md
2. **Learn**: OTP_INTEGRATION_GUIDE.md
3. **Implement**: OTP_CODE_EXAMPLES.md
4. **Reference**: OTP_IMPLEMENTATION_REFERENCE.md
5. **Overview**: OTP_SUMMARY.md

## ✨ Next Features

- [ ] Rate limiting
- [ ] Email verification
- [ ] Two-factor auth
- [ ] Backup codes
- [ ] OTP history
- [ ] Admin dashboard
- [ ] WhatsApp OTP
- [ ] TOTP support

## 🎉 You're Ready!

```bash
python manage.py migrate     # Setup database
python manage.py runserver   # Start server
# Visit http://localhost:8000/otp/request/
```

**Happy coding! 🚀**
