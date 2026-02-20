# OTP Integration - Quick Setup Checklist

## ✅ What's Been Done

- [x] Added OTP model with email/phone support
- [x] Created OTP utilities for generation and sending
- [x] Implemented OTP views (request, verify, resend, logout)
- [x] Created OTP forms with validation
- [x] Created OTP templates (request & verify pages)
- [x] Updated Django settings with email config
- [x] Added URL routes for OTP authentication
- [x] Added comprehensive documentation

## 🔧 What You Need to Do

### 1. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Configure Email (Choose One)

**Development (Recommended for Testing)**
```python
# Already configured in settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Gmail**
1. Go to: https://myaccount.google.com/apppasswords
2. Create app password
3. Update in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

**Other SMTP Provider**
Update EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

### 3. (Optional) Install SMS Package
```bash
pip install twilio
```

Then configure Twilio in `settings.py`

### 4. Test the Integration

**Step 1: Create a test customer**
```bash
python manage.py shell
from core.models import Customer
Customer.objects.create(
    name='Test Customer',
    email='test@example.com',
    phone='9876543210',
    customer_type='Household'
)
```

**Step 2: Visit OTP page**
- Open browser: `http://localhost:8000/otp/request/`
- Select email option
- Enter test customer's email
- Click "Request OTP"

**Step 3: Check console/email**
- Development: Check Django console for OTP code
- Production: Check your email inbox

**Step 4: Verify OTP**
- Enter the 6-digit code on next page
- Click "Verify & Login"

## 📝 File Structure

```
core/
├── models.py                 (Updated: Added OTP model)
├── views.py                  (Updated: Added OTP views)
├── forms.py                  (Updated: Added OTP forms)
├── urls.py                   (Updated: Added OTP routes)
├── otp_utils.py             (New: OTP utilities)
└── templates/
    └── core/
        ├── request_otp.html  (New: Request OTP page)
        └── verify_otp.html   (New: Verify OTP page)

waste_billing/
└── settings.py              (Updated: Email config)

OTP_INTEGRATION_GUIDE.md     (New: Full documentation)
OTP_SETUP_CHECKLIST.md       (New: This file)
```

## 🔐 Security Checklist

- [ ] Use HTTPS in production
- [ ] Don't log OTP codes in production
- [ ] Keep email credentials secure
- [ ] Test rate limiting
- [ ] Monitor failed attempts
- [ ] Keep customer email/phone updated

## 🧪 Testing Scenarios

### Scenario 1: Successful OTP Login
1. Request OTP
2. Enter correct 6-digit code
3. ✅ Should redirect to customer dashboard

### Scenario 2: Expired OTP
1. Request OTP
2. Wait 5+ minutes
3. Enter OTP
4. ❌ Should show "OTP has expired"

### Scenario 3: Invalid OTP
1. Request OTP
2. Enter wrong code
3. ❌ Should show "Invalid OTP"
4. Attempts should decrease

### Scenario 4: Max Attempts Exceeded
1. Request OTP
2. Enter wrong code 5 times
3. ❌ Should show "Too many attempts"

### Scenario 5: Resend OTP
1. Request OTP
2. Click Resend OTP
3. ✅ Should receive new OTP
4. Old OTP should be invalid

## 📞 Email Provider Setup Examples

### Gmail Setup Steps
1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character password
4. Use as `EMAIL_HOST_PASSWORD`

### SendGrid Setup
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
DEFAULT_FROM_EMAIL = 'your-email@example.com'
```

### AWS SES Setup
```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
```

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: No module named 'otp_utils'" | Run migrations and restart Django |
| "Emails not sending" | Check EMAIL_BACKEND and credentials |
| "Customer not found" | Verify customer email/phone in database |
| "OTP form not displaying" | Check base.html is being used in templates |
| "CSRF token missing" | Ensure `{% csrf_token %}` in form |
| "Database error" | Run `python manage.py migrate` |

## 🚀 Next Steps (Optional)

1. **Add Rate Limiting**: Limit OTP requests per user
2. **Add Email Verification**: Verify email when customer created
3. **Add Two-Factor Auth**: Combine OTP with password
4. **Add OTP History**: Keep audit log of OTP usage
5. **Add Admin Dashboard**: View OTP attempts and stats
6. **Add SMS Gateway**: Integrate with SMS provider
7. **Add QR Code OTP**: TOTP-based authentication

## 📚 Resources

- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- [Twilio SMS Documentation](https://www.twilio.com/docs/sms)
- [OTP Best Practices](https://owasp.org/www-community/attacks/Brute_force_attack)

## ❓ FAQ

**Q: Can I use the same OTP for email and phone?**
A: No, each request generates a unique OTP. You need to request a new one for a different contact method.

**Q: Is OTP stored in plain text?**
A: Yes, for simplicity. In production, consider hashing the OTP.

**Q: Can I change OTP length?**
A: Yes, modify `generate_otp()` in `otp_utils.py`

**Q: How to integrate with existing login?**
A: Add OTP as second factor after password verification.

**Q: Can I customize OTP message?**
A: Yes, modify templates in `otp_utils.py` email functions.

---

**Need Help?** Check OTP_INTEGRATION_GUIDE.md for detailed documentation.
