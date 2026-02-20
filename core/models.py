from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# -------------------------
# Customer Model
# -------------------------
class Customer(models.Model):
    CUSTOMER_TYPES = [
        ('Household', 'Household'),
        ('Shop', 'Shop'),
        ('Hotel', 'Hotel'),
    ]
    customer_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20,default='N/A')
    address = models.CharField(max_length=255, default='N/A')
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='Household')
    monthly_rate = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Generate customer_id if not provided
            import random
            import string
            self.customer_id = 'CUST' + ''.join(random.choices(string.digits, k=6))

        if self.customer_type == 'Household':
            self.monthly_rate = 300
        elif self.customer_type == 'Shop':
            self.monthly_rate = 500
        elif self.customer_type == 'Hotel':
            self.monthly_rate = 1000
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_id} - {self.name}"

# -------------------------
# Waste Item Model
# -------------------------
class WasteItem(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.name

# -------------------------
# Bill Model
# -------------------------
class Bill(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_amount = models.FloatField(default=0)
    status = models.CharField(max_length=50, choices=[('Paid','Paid'),('Unpaid','Unpaid')], default='Unpaid')
    paid = models.BooleanField(default=False)
    month = models.IntegerField(default=timezone.now().month)
    year = models.IntegerField(default=timezone.now().year)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id} - {self.customer.name} ({self.customer.customer_type})"

    def recalc_total(self):
        total = sum(item.amount for item in self.items.all()) if hasattr(self, 'items') else self.total_amount
        self.total_amount = total
        self.save()

# -------------------------
# Bill Item Model
# -------------------------
class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    waste_item = models.ForeignKey(WasteItem, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.amount = (self.waste_item.unit_price or 0) * (self.quantity or 0)
        super().save(*args, **kwargs)
        self.bill.recalc_total()

    def __str__(self):
        return f"{self.waste_item.name} x {self.quantity}"

# -------------------------
# Feedback Model
# -------------------------
class Feedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback #{self.id}"

# -------------------------
# OTP Model
# -------------------------
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
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        contact = self.email if self.otp_type == 'email' else self.phone
        return f"OTP for {contact} ({self.otp_type})"
    
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


# -------------------------
# Sent Email (Development Outbox)
# -------------------------
class SentEmail(models.Model):
    """Stores sent email content for development/debugging (outbox)."""
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    html_body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Email to {self.to_email} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
