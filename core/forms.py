from django import forms
from .models import Feedback
from .models import Customer
from .models import Bill, OTP
import re
from django.contrib.auth.hashers import make_password



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['customer', 'comment']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write feedback here...'
            }),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')

        if not comment:
            raise forms.ValidationError("Feedback cannot be empty.")

        if len(comment.strip()) < 5:
            raise forms.ValidationError("Feedback must be at least 5 characters long.")

        return comment
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_id',
            'name',
            'email',
            'phone',
            'address',
            'customer_type',
            'monthly_rate'
        ]
    widgets = {
            'customer_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name',
            }),
        }

    # 1️⃣ Customer ID validation
    def clean_customer_id(self):
        customer_id = self.cleaned_data.get('customer_id')

        if customer_id:
            # Check if customer_id is unique (excluding current instance)
            existing_customer = Customer.objects.filter(customer_id=customer_id).first()
            if existing_customer and existing_customer.pk != self.instance.pk:
                raise forms.ValidationError("This customer ID is already in use.")

            # Validate format (should start with CUST followed by 6 digits)
            if not customer_id.startswith('CUST') or not customer_id[4:].isdigit() or len(customer_id) != 10:
                raise forms.ValidationError("Customer ID must be in format CUSTXXXXXX (CUST followed by 6 digits).")

        return customer_id

    # 2️⃣ Name validation
    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not name or name.strip() == "":
            raise forms.ValidationError("Customer name is required.")

        if len(name.strip()) < 3:
            raise forms.ValidationError("Customer name must be at least 3 characters long.")

        if name.isdigit():
            raise forms.ValidationError("Customer name cannot contain only numbers.")

        return name.strip()

    # 3️⃣ Email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError("Email is required.")

        # Optional but STRONGLY recommended
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")

        return email

    # 4️⃣ Phone validation
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if phone:
            if not phone.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")

            if len(phone) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")

            # Check if phone number is unique
            existing_customer = Customer.objects.filter(phone=phone).first()
            if existing_customer and existing_customer.pk != self.instance.pk:
                raise forms.ValidationError("This phone number is already registered.")

        return phone

    # 5️⃣ Address validation
    def clean_address(self):
        address = self.cleaned_data.get('address')

        if not address or address.strip() == "":
            raise forms.ValidationError("Address is required.")

        if len(address.strip()) < 5:
            raise forms.ValidationError("Address must be at least 5 characters long.")

        return address.strip()

    # 6️⃣ Customer type validation
    def clean_customer_type(self):
        customer_type = self.cleaned_data.get('customer_type')

        if not customer_type:
            raise forms.ValidationError("Please select a customer type.")

        return customer_type

    # 7️⃣ Monthly rate validation
    def clean_monthly_rate(self):
        rate = self.cleaned_data.get('monthly_rate')

        if rate is None:
            raise forms.ValidationError("Monthly rate is required.")

        if rate < 0:
            raise forms.ValidationError("Monthly rate cannot be negative.")

        return rate

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['customer', 'total_amount', 'status', 'paid']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # 1️⃣ Customer validation
    def clean_customer(self):
        customer = self.cleaned_data.get('customer')

        if not customer:
            raise forms.ValidationError("Customer is required.")

        return customer

    # 2️⃣ Total amount validation
    def clean_total_amount(self):
        total_amount = self.cleaned_data.get('total_amount')

        if total_amount is None:
            raise forms.ValidationError("Total amount is required.")

        if total_amount <= 0:
            raise forms.ValidationError("Total amount must be greater than zero.")

        return total_amount

    # 3️⃣ Status validation
    def clean_status(self):
        status = self.cleaned_data.get('status')

        valid_status = ['Paid', 'Unpaid']
        if status not in valid_status:
            raise forms.ValidationError("Invalid bill status.")

        return status


# ========================
# OTP FORMS
# ========================

class RequestOTPForm(forms.Form):
    """Form to request OTP via email or phone"""
    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone Number'),
    ]
    
    contact_type = forms.ChoiceField(
        choices=CONTACT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="How would you like to receive OTP?"
    )
    
    contact_value = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email or phone number',
            'id': 'contact_value'
        }),
        label="Email or Phone Number"
    )
    
    def clean_contact_value(self):
        contact_value = self.cleaned_data.get('contact_value')
        contact_type = self.cleaned_data.get('contact_type')
        
        if not contact_value:
            raise forms.ValidationError("Please enter your contact information.")
        
        if contact_type == 'email':
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, contact_value):
                raise forms.ValidationError("Please enter a valid email address.")
            
            # Check if customer exists with this email
            if not Customer.objects.filter(email=contact_value).exists():
                raise forms.ValidationError("No customer found with this email.")
        
        elif contact_type == 'phone':
            # Validate phone format (10 digits)
            if not contact_value.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            
            if len(contact_value) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
            
            # Check if customer exists with this phone
            if not Customer.objects.filter(phone=contact_value).exists():
                raise forms.ValidationError("No customer found with this phone number.")
        
        return contact_value


class VerifyOTPForm(forms.Form):
    """Form to verify OTP"""
    
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'id': 'otp_input'
        }),
        label="Enter OTP"
    )
    
    def clean_otp_code(self):
        otp_code = self.cleaned_data.get('otp_code')
        
        if not otp_code:
            raise forms.ValidationError("Please enter the OTP.")
        
        if not otp_code.isdigit():
            raise forms.ValidationError("OTP must contain only digits.")
        
        if len(otp_code) != 6:
            raise forms.ValidationError("OTP must be exactly 6 digits.")
        
        return otp_code


class OTPModelForm(forms.ModelForm):
    """Admin form for OTP model"""
    
    class Meta:
        model = OTP
        fields = ['email', 'phone', 'otp_code', 'otp_type', 'is_verified']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'otp_code': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'otp_type': forms.Select(attrs={'class': 'form-control'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
