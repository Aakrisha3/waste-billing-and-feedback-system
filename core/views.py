from django.shortcuts import render, redirect, get_object_or_404
from .models import Feedback, Bill, BillItem, WasteItem, Customer
from .forms import FeedbackForm
from .forms import CustomerForm
from .models import Customer
from django.utils import timezone
from .forms import BillForm 

def home(request):
    total_customers = Customer.objects.count()
    total_bills = Bill.objects.count()
    total_feedbacks = Feedback.objects.count()
    context = {
        'total_customers': total_customers,
        'total_bills': total_bills,
        'total_feedbacks': total_feedbacks
    }
    return render(request, 'core/home.html', context)

def feedback_list(request):
	feedbacks = Feedback.objects.order_by('-created_at')
	return render(request, 'core/feedback_list.html', {'feedbacks': feedbacks})

def add_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedback_list')
    else:
        form = FeedbackForm()
    return render(request, 'core/add_feedback.html', {'form': form})

def feedback_create(request):
	if request.method == 'POST':
		form = FeedbackForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('core:feedback_list')
	else:
		form = FeedbackForm()
	return render(request, 'core/feedback_form.html', {'form': form})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'core/customers.html', {'customers': customers})

def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Redirect to homepage after adding
    else:
        form = CustomerForm()
    return render(request, 'core/add_customer.html', {'form': form})

# Edit customer
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('core:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'core/add_customer.html', {'form': form})

# Delete customer
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    return redirect('core:customer_list')

# View customer details
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    bills = customer.bill_set.all()  # All bills of this customer
    return render(request, 'core/customer_detail.html', {'customer': customer, 'bills': bills})

def bill_list(request):
    bills = Bill.objects.all()
    return render(request, 'core/bill_list.html', {'bills': bills})

def add_bill(request):
    customers = Customer.objects.all()
    waste_items = WasteItem.objects.all()
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(Customer, id=customer_id)
        
        # Create the Bill with month and year
        now = timezone.now()
        bill = Bill.objects.create(
            customer=customer,
            total_amount=0,
            paid=False,
            month=now.strftime("%B"),  # e.g., "October"
            year=now.year
        )
        
        total = 0
        for item in waste_items:
            qty = request.POST.get(f'quantity_{item.id}')
            if qty:
                qty = float(qty)  # use float for decimal quantities
                # Create BillItem and calculate amount
                BillItem.objects.create(bill=bill, waste_item=item, quantity=qty)
                total += (item.unit_price or 0) * qty  # use unit_price
        
        bill.total_amount = total
        bill.save()
        return redirect('bill_list')
    
    return render(request, 'core/add_bill.html', {'customers': customers, 'waste_items': waste_items})

def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    items = BillItem.objects.filter(bill=bill)
    return render(request, 'core/bill_detail.html', {'bill': bill, 'items': items})

def edit_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            return redirect('core:bill_list')
    else:
        form = BillForm(instance=bill)
    return render(request, 'core/edit_bill.html', {'form': form, 'bill': bill})


def delete_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill.delete()
    return redirect('core:bill_list')