# OTP Integration - Migration & Setup Guide

## Step-by-Step Migration Process

### Phase 1: Pre-Migration Checks

#### 1.1 Verify Django is Running
```bash
# Check Django version
python manage.py --version
# Expected: 4.2 or higher
```

#### 1.2 Backup Database
```bash
# SQLite backup
cp db.sqlite3 db.sqlite3.backup

# For production, take proper backups
```

#### 1.3 Check Current Migrations
```bash
python manage.py showmigrations
# Should show all migrations applied
```

---

### Phase 2: Create Migrations

#### 2.1 Generate Migration File
```bash
python manage.py makemigrations core
```

**Expected Output:**
```
Migrations for 'core':
  0013_otp.py
    - Create model OTP
```

#### 2.2 Verify Migration File
```bash
# Check if migration was created
ls core/migrations/00*.py | tail -1

# You should see: 0013_otp.py (or similar)
```

#### 2.3 View Migration Content
```bash
cat core/migrations/0013_otp.py
# Should contain CreateModel operation for OTP
```

---

### Phase 3: Apply Migrations

#### 3.1 Run Migrations
```bash
python manage.py migrate core
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, messages, staticfiles, core
Running migrations:
  Applying core.0013_otp... OK
```

#### 3.2 Verify Migration Applied
```bash
python manage.py showmigrations core
```

**Expected Output:**
```
core
 [X] 0001_initial
 [X] 0002_customer_wasteitem_and_more
 ...
 [X] 0013_otp
```

---

### Phase 4: Verify Database

#### 4.1 Check Table Creation
```bash
python manage.py dbshell
# SQLite prompt

# List tables
.tables

# You should see: core_otp

# Check OTP table structure
.schema core_otp

# Exit
.quit
```

#### 4.2 Verify Table Columns
Expected columns in `core_otp`:
- id
- email
- phone
- otp_code
- otp_type
- is_verified
- created_at
- expires_at
- attempts
- max_attempts

---

### Phase 5: Test OTP Model

#### 5.1 Test Model Import
```bash
python manage.py shell
```

```python
from core.models import OTP
print("OTP model imported successfully")

# Check model fields
OTP._meta.get_fields()
# Should show all OTP fields
```

#### 5.2 Create Test OTP Record
```python
from django.utils import timezone
from datetime import timedelta

# Create test OTP
otp = OTP.objects.create(
    email='test@example.com',
    otp_code='123456',
    otp_type='email',
    expires_at=timezone.now() + timedelta(minutes=5)
)

print(f"Created OTP: {otp.id}")

# Retrieve and verify
otp = OTP.objects.get(id=1)
print(f"Email: {otp.email}")
print(f"OTP Code: {otp.otp_code}")
```

#### 5.3 Test OTP Methods
```python
otp = OTP.objects.first()

# Test is_valid()
print(f"Is valid: {otp.is_valid()}")

# Test is_expired()
print(f"Is expired: {otp.is_expired()}")

# Test verify()
result = otp.verify('123456')
print(f"Verification result: {result}")
```

#### 5.4 Clean Up Test Data
```python
OTP.objects.all().delete()
exit()
```

---

### Phase 6: Test OTP Utilities

#### 6.1 Test Import
```bash
python manage.py shell
```

```python
from core.otp_utils import *

print("All OTP utilities imported successfully")
```

#### 6.2 Test OTP Generation
```python
code = generate_otp()
print(f"Generated OTP: {code}")
print(f"Length: {len(code)}")
print(f"Is digit: {code.isdigit()}")
```

#### 6.3 Test OTP Creation
```python
otp = create_otp(
    email='test@example.com',
    otp_type='email',
    expiry_minutes=5
)
print(f"Created OTP: {otp.otp_code}")
print(f"Expires at: {otp.expires_at}")
```

#### 6.4 Test OTP Verification
```python
# Correct code
result = verify_otp('test@example.com', otp.otp_code, 'email')
print(f"Correct code result: {result}")

# Verify OTP object
otp_obj = OTP.objects.get(email='test@example.com')
print(f"Is verified: {otp_obj.is_verified}")

# Clean up
OTP.objects.all().delete()
exit()
```

---

### Phase 7: Configure Email

#### 7.1 Choose Email Provider

**Option A: Development (Console)**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@wastebilling.local'
```

**Option B: Gmail**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'app-password-16-chars'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

#### 7.2 Test Email Configuration
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

# Test email
success = send_mail(
    'Test OTP Subject',
    'Test OTP Message',
    'noreply@wastebilling.local',
    ['test@example.com'],
    fail_silently=False,
)

print(f"Email sent: {success}")
exit()
```

---

### Phase 8: Test Views

#### 8.1 Create Test Customer
```bash
python manage.py shell
```

```python
from core.models import Customer

# Create test customer
customer = Customer.objects.create(
    name='Test User',
    email='test@example.com',
    phone='9876543210',
    customer_type='Household'
)

print(f"Created customer: {customer.id}")
exit()
```

#### 8.2 Start Development Server
```bash
python manage.py runserver
```

#### 8.3 Test Request OTP Page
```
Visit: http://localhost:8000/otp/request/

Expected:
- Radio buttons for email/phone
- Contact input field
- Submit button
- Responsive design
```

#### 8.4 Test Request OTP Flow
```
1. Select: Email
2. Enter: test@example.com
3. Click: Request OTP
4. Expected: Redirect to verify page
   Console should show email content
```

#### 8.5 Test Verify OTP Page
```
Visit: http://localhost:8000/otp/verify/
(After requesting OTP)

Expected:
- OTP input field (6 digits)
- Verify button
- Resend button
- Change contact button
```

#### 8.6 Test Verify OTP Flow
```
1. Check console for OTP code
2. Copy OTP code
3. Paste in input field
4. Click: Verify & Login
5. Expected: Success message
```

---

### Phase 9: Test Forms

#### 9.1 Test Request OTP Form
```bash
python manage.py shell
```

```python
from core.forms import RequestOTPForm

# Valid data
form = RequestOTPForm(data={
    'contact_type': 'email',
    'contact_value': 'test@example.com'
})

print(f"Form valid: {form.is_valid()}")
print(f"Cleaned data: {form.cleaned_data}")
```

#### 9.2 Test Verify OTP Form
```python
from core.forms import VerifyOTPForm

# Valid data
form = VerifyOTPForm(data={
    'otp_code': '123456'
})

print(f"Form valid: {form.is_valid()}")

# Invalid data (short)
form = VerifyOTPForm(data={
    'otp_code': '123'
})

print(f"Form valid: {form.is_valid()}")
print(f"Errors: {form.errors}")

exit()
```

---

### Phase 10: Run Full Test Suite

#### 10.1 Create Test Case
```bash
# Create test file: core/test_otp.py
```

```python
from django.test import TestCase
from core.models import Customer, OTP
from core.otp_utils import create_otp, verify_otp

class OTPTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test',
            email='test@example.com',
            phone='9876543210'
        )
    
    def test_create_otp(self):
        otp = create_otp(email=self.customer.email)
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.otp_code), 6)
    
    def test_verify_otp(self):
        otp = create_otp(email=self.customer.email)
        result = verify_otp(self.customer.email, otp.otp_code, 'email')
        self.assertTrue(result['success'])
```

#### 10.2 Run Tests
```bash
python manage.py test core.test_otp
```

**Expected Output:**
```
Ran 2 tests in 0.XXXs
OK
```

---

### Phase 11: Rollback Plan (If Needed)

#### 11.1 Rollback Last Migration
```bash
# Unapply last migration
python manage.py migrate core 0012

# Verify
python manage.py showmigrations core
```

#### 11.2 Delete Migration File
```bash
# Remove migration file
rm core/migrations/0013_otp.py
```

#### 11.3 Restore Database
```bash
# Restore from backup
cp db.sqlite3.backup db.sqlite3
```

---

### Phase 12: Production Deployment

#### 12.1 Pre-Deployment Checklist
- [ ] All tests pass
- [ ] Email configured for production
- [ ] Database backed up
- [ ] SECRET_KEY updated
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled

#### 12.2 Deploy Steps
```bash
# 1. Pull latest code
git pull origin main

# 2. Run migrations
python manage.py migrate

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Restart application server
# (supervisor, systemd, etc.)
```

#### 12.3 Post-Deployment Verification
```bash
# Check if OTP table exists
python manage.py dbshell
.schema core_otp
.quit

# Test OTP creation
python manage.py shell
from core.otp_utils import create_otp
otp = create_otp(email='admin@example.com')
print(f"OTP created: {otp.otp_code}")
exit()
```

---

## Troubleshooting Migration Issues

### Issue 1: Duplicate Migrations
```
Error: Conflicting migrations detected
```

**Solution:**
```bash
# Check migration status
python manage.py showmigrations core

# Manually remove duplicate
# (Only if you know what you're doing)
rm core/migrations/0013_otp.py
python manage.py makemigrations core
```

### Issue 2: Migration Not Applied
```
Error: No such table: core_otp
```

**Solution:**
```bash
# Check migrations
python manage.py showmigrations core

# Apply unapplied migrations
python manage.py migrate core

# Verify
python manage.py showmigrations core
```

### Issue 3: Database Locked
```
Error: database is locked
```

**Solution:**
```bash
# Close all connections
# Restart Django

# Or, remove lock file
# (For SQLite only)
rm -f db.sqlite3-wal
rm -f db.sqlite3-shm
```

### Issue 4: Column Already Exists
```
Error: duplicate column name
```

**Solution:**
```bash
# Rollback and check
python manage.py migrate core 0012

# Manually check database
python manage.py dbshell
.schema core_otp
.quit

# Delete if needed (data loss!)
python manage.py shell
OTP.objects.all().delete()
exit()
```

---

## Verification Checklist

- [ ] Migration file created
- [ ] Migration applied successfully
- [ ] OTP table exists in database
- [ ] OTP model imported successfully
- [ ] OTP utilities work
- [ ] Views accessible
- [ ] Forms validate
- [ ] Email configured
- [ ] Tests pass
- [ ] No errors in console

---

## Performance Tips

1. **Add Database Indexes**
   ```python
   # In OTP model Meta class
   class Meta:
       indexes = [
           models.Index(fields=['email']),
           models.Index(fields=['phone']),
           models.Index(fields=['created_at']),
       ]
   ```

2. **Clean Up Expired OTPs**
   ```bash
   # Create management command to run daily
   python manage.py cleanup_otps
   ```

3. **Cache Customer Lookups**
   ```python
   from django.views.decorators.cache import cache_page
   
   @cache_page(60)
   def request_otp(request):
       # ...
   ```

---

## Monitoring

### Check OTP Statistics
```bash
python manage.py shell
```

```python
from core.models import OTP
from django.utils import timezone
from datetime import timedelta

# Total OTPs
total = OTP.objects.count()

# Today's OTPs
today = OTP.objects.filter(
    created_at__date=timezone.now().date()
).count()

# Verified
verified = OTP.objects.filter(is_verified=True).count()

# Expired
expired = OTP.objects.filter(
    expires_at__lt=timezone.now()
).count()

print(f"Total: {total}")
print(f"Today: {today}")
print(f"Verified: {verified}")
print(f"Expired: {expired}")
```

---

You're all set for migration! 🚀
