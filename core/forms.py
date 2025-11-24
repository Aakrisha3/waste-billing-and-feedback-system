from django import forms
from .models import Feedback
from .models import Customer
from .models import Bill



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['customer', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write feedback here...'}),
        }
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'customer_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
        }

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['customer', 'total_amount', 'paid']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
