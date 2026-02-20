# 🔐 Admin OTP Login Integration - Updated Guide

## Overview

The OTP authentication system has been **integrated into the admin login process**. Admins now need to:
1. Enter username, password, AND email
2. Receive an OTP code via email
3. Verify the OTP to complete login

---

## 🔄 Admin Login Flow

```
┌─────────────────────────────────────────────────────────┐
│           ADMIN LOGIN WITH OTP FLOW                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Admin visits /login/                               │
│     └─→ Enter: Username, Password, Email              │
│                                                         │
│  2. System validates credentials                       │
│     ├─ Check username/password correct                │
│     ├─ Verify user is admin/staff                      │
│     └─ Verify email provided                           │
│                                                         │
│  3. Generate OTP                                        │
│     ├─ Create 6-digit random code                     │
│     ├─ Set 5-minute expiration                         │
│     └─ Store in database                               │
│                                                         │
│  4. Send via Email                                      │
│     └─→ Admin receives OTP code                        │
│                                                         │
│  5. Redirect to /verify-otp/                           │
│     └─→ Admin enters 6-digit code                     │
│                                                         │
│  6. Verify OTP                                          │
│     ├─ Check code matches                              │
│     ├─ Check not expired                               │
│     └─ Check attempts < 5                              │
│                                                         │
│  7. SUCCESS: Login & Redirect                          │
│     ├─ Set session for admin                           │
│     ├─ Clear OTP session data                          │
│     └─→ Redirect to dashboard                          │
│                                                         │
│  OR FAILURE: Show Error                                │
│     ├─ Invalid code: Show error                        │
│     ├─ Expired: Show error + resend option            │
│     └─ Max attempts: Redirect to login                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📍 Key Changes

### 1. **Login Page** (/login/)
- **Before**: Username + Password only
- **After**: Username + Password + Email

### 2. **New OTP Verification Page** (/verify-otp/)
- Displays masked email
- OTP input field (6 digits)
- Resend option
- Back to login option
- Attempt counter (max 5)

### 3. **Backend Routes**
```
/login/        → Admin login form (POST to admin_login view)
/verify-otp/   → OTP verification page (POST to admin_verify_otp view)
/resend-otp/   → Resend OTP (GET request to admin_resend_otp view)
/logout/       → Logout (admin_logout view)
```

### 4. **Views Updated**
- `admin_login()` - Now sends OTP instead of login
- `admin_verify_otp()` - New view for OTP verification
- `admin_resend_otp()` - New view to resend OTP
- `admin_logout()` - Unchanged

---

## 🔐 Security Features

✅ **Email Required** - Ensures admin can receive OTP  
✅ **OTP Expiration** - 5 minute validity period  
✅ **Attempt Limiting** - Max 5 wrong attempts  
✅ **Session Management** - Secure session handling  
✅ **Clear Separation** - Distinguishes OTP data per attempt  
✅ **Error Messages** - Informative but not revealing  

---

## 🚀 Quick Setup

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Configure Email
In `settings.py`:
```python
# Development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Production (Gmail example)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@gmail.com'
EMAIL_HOST_PASSWORD = 'app-password'
DEFAULT_FROM_EMAIL = 'your@gmail.com'
```

### 3. Test Login
1. Visit `/login/`
2. Enter admin username & password
3. Enter admin email
4. Click "Login & Verify OTP"
5. Check email/console for OTP
6. Enter OTP code
7. Click "Verify & Login"

---

## 📋 Admin Login Process (Step by Step)

### Step 1: Login Page
```
Admin visits: http://localhost:8000/login/

Form has 3 fields:
├─ Username: admin123
├─ Password: ••••••••
└─ Email: admin@example.com

Click: "Login & Verify OTP"
```

### Step 2: OTP Generation
```
Backend validates credentials
├─ Check username/password
├─ Verify admin/staff user
└─ Generate & send OTP

If successful:
├─ Create OTP record in DB
├─ Send email with code
└─ Redirect to /verify-otp/
```

### Step 3: OTP Verification Page
```
Shows: admin@example.com

Admin sees:
├─ "OTP Sent!" message
├─ 6-digit input field
├─ "Verify & Login" button
├─ "Back to Login" button
└─ "Resend OTP" button
```

### Step 4: Verify OTP
```
Admin checks email for code: 123456

Admin enters code and clicks verify

Backend:
├─ Checks code matches
├─ Checks not expired (5 min)
├─ Checks attempts < 5
└─ If valid: Login admin user
```

### Step 5: Success
```
✅ Login successful
├─ Session created for admin
├─ OTP session data cleared
└─ Redirect to dashboard
```

---

## 🔄 Resend OTP Flow

**If Admin Doesn't Receive Email:**

1. Click "Resend OTP" button
2. System generates new code
3. Old code becomes invalid
4. New email sent
5. Attempt counter resets

---

## ⚠️ Error Scenarios

### Invalid OTP
```
Message: "Invalid OTP. Attempts remaining: 4"
Action: Admin can retry
```

### Expired OTP
```
Message: "OTP has expired. Please request a new one."
Action: Resend OTP option available
```

### Max Attempts Exceeded
```
Message: "Too many failed attempts. Please login again."
Action: Redirect to login page, must restart process
```

### Session Expired
```
Message: "Session expired. Please login again."
Action: Redirect to login page
```

---

## 📊 Database Changes

### OTP Table
```sql
CREATE TABLE core_otp (
    id INTEGER PRIMARY KEY,
    email VARCHAR(254),
    phone VARCHAR(20),
    otp_code VARCHAR(6),
    otp_type VARCHAR(10),  -- 'email' or 'phone'
    is_verified BOOLEAN,
    created_at DATETIME,
    expires_at DATETIME,
    attempts INTEGER,
    max_attempts INTEGER
);
```

### Example Admin Login OTP Record
```
email: admin@example.com
phone: NULL
otp_code: 123456
otp_type: email
is_verified: FALSE → TRUE (after verification)
created_at: 2025-02-10 10:30:00
expires_at: 2025-02-10 10:35:00
attempts: 0 → 1 (after wrong attempt)
max_attempts: 5
```

---

## 🧪 Testing Checklist

- [ ] Run migrations successfully
- [ ] Email configured (console or SMTP)
- [ ] Admin account exists (staff=True)
- [ ] Visit /login/ - shows email field
- [ ] Enter valid credentials
- [ ] OTP sent to console/email
- [ ] Can enter OTP code
- [ ] Correct code logs in admin
- [ ] Wrong code shows error
- [ ] Max attempts redirects
- [ ] Resend creates new OTP
- [ ] Sessions work correctly
- [ ] Mobile responsive design

---

## 📧 Email Content

**Subject:** Admin Login OTP

**Body (HTML formatted):**
```
Admin Login Verification

Your One-Time Password (OTP) for Waste Billing Admin Login is:

    123456

This code is valid for 5 minutes only.
Do not share this code with anyone.

If you didn't request this login, please ignore this email.

---
Waste Billing Management System
```

---

## 🔍 URL Reference

| Route | Method | Purpose |
|-------|--------|---------|
| `/login/` | GET | Show login form |
| `/login/` | POST | Process login & send OTP |
| `/verify-otp/` | GET | Show OTP verification form |
| `/verify-otp/` | POST | Verify OTP code |
| `/resend-otp/` | GET | Resend OTP |
| `/logout/` | GET | Logout admin |

---

## 💾 Session Data During Process

### After Successful Credential Verification
```python
request.session = {
    'pending_admin_username': 'admin',
    'pending_admin_email': 'admin@example.com',
    'pending_admin_user_id': 1,
    'otp_attempt': 0
}
```

### After OTP Verification Success
```python
# Session cleared
request.session = {}  # Admin is logged in via login()
```

---

## 🛡️ Security Best Practices

1. **Email Configuration**
   - Use SMTP in production (not console)
   - Use TLS/SSL encryption
   - Use app-specific passwords

2. **OTP Storage**
   - OTP codes stored in database
   - Not logged in plain text
   - Automatically cleaned after expiration

3. **Session Management**
   - Session data cleared after OTP verification
   - Session timeout prevents unauthorized access
   - No sensitive data in session

4. **Attempt Limiting**
   - Maximum 5 wrong attempts
   - Forces re-login after max attempts
   - Prevents brute force attacks

---

## 🔧 Customization Options

### Change OTP Expiry Time
**File:** `core/otp_utils.py`
```python
def create_otp(..., expiry_minutes=10):  # Change from 5 to 10
    ...
```

### Change Max Attempts
**File:** `core/models.py`
```python
max_attempts = models.IntegerField(default=10)  # Change from 5 to 10
```

### Customize Email Template
**File:** `core/otp_utils.py`
```python
def send_otp_email(...):
    # Modify message and html_message
```

### Change OTP Length
**File:** `core/otp_utils.py`
```python
def generate_otp():
    return ''.join(random.choices(string.digits, k=8))  # 8 digits
```

---

## ✅ Verification Steps

### Step 1: Check Database
```bash
python manage.py shell
from core.models import OTP
OTP.objects.all()  # Should see OTP records after login attempt
```

### Step 2: Check Email
```
Development: Check Django console for email content
Production: Check email inbox
```

### Step 3: Check Session
```bash
python manage.py shell
# After OTP verification, request.session should have user
```

---

## 📞 Troubleshooting

### "Email field not showing"
- Clear browser cache
- Hard refresh (Ctrl+F5)
- Check template file exists

### "OTP not arriving"
- Check email configuration in settings.py
- Check console output (development)
- Check spam folder (production)
- Verify admin email address

### "Can't login after OTP"
- Verify OTP matches exactly
- Check OTP hasn't expired
- Check not exceeded 5 attempts
- Try resending OTP

### "Session errors"
- Clear session/cookies
- Restart Django server
- Check database migrations

---

## 📈 Next Steps

1. ✅ Run migrations
2. ✅ Configure email
3. ✅ Test admin login
4. ✅ Deploy to production
5. ✅ Monitor usage

---

## 🎯 Summary

**Admin Login Now:**
1. Requires email address
2. Sends OTP verification code
3. Requires OTP verification
4. Provides secure two-factor verification

**Key Benefits:**
- ✅ Enhanced security
- ✅ Prevents unauthorized access
- ✅ Audit trail of logins
- ✅ User receives notification

---

**Implementation Complete!** 🎉

Your Waste Billing System now has secure admin login with OTP verification.
