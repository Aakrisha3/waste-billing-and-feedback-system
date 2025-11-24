from django.db import models
from django.utils import timezone

# -------------------------
# Customer Model
# -------------------------
class Customer(models.Model):
    CUSTOMER_TYPES = [
        ('Household', 'Household'),
        ('Shop', 'Shop'),
        ('Hotel', 'Hotel'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20,default='N/A')
    address = models.CharField(max_length=255, default='N/A')
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='Household')
    monthly_rate = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if self.customer_type == 'Household':
            self.monthly_rate = 300
        elif self.customer_type == 'Shop':
            self.monthly_rate = 500
        elif self.customer_type == 'Hotel':
            self.monthly_rate = 1000
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

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
