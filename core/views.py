from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Feedback, Bill, BillItem, WasteItem, Customer, OTP
from .forms import FeedbackForm
from .forms import CustomerForm
from .models import Customer
from django.utils import timezone
from .forms import BillForm
from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
import qrcode
from io import BytesIO
from .otp_utils import create_otp, send_otp_email, send_otp_sms, verify_otp
from django.conf import settings

# Authentication Views
def admin_login(request):
    """Admin login with email and OTP verification"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        # Validate credentials first
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:  # Only allow staff/admin users
            # Check if email is provided
            if not email:
                messages.error(request, 'Please provide your email address.')
                return render(request, 'core/login.html')
            
            # Create and send OTP
            otp = create_otp(
                email=email,
                otp_type='email',
                expiry_minutes=5
            )
            
            # Send OTP via email
            success = send_otp_email(email, otp.otp_code, user.first_name or user.username)
            
            if success:
                # Store user and email in session for OTP verification
                request.session['pending_admin_username'] = username
                request.session['pending_admin_email'] = email
                request.session['pending_admin_user_id'] = user.id
                request.session['otp_attempt'] = 0
                
                messages.success(request, f'OTP sent to {email}. Please verify to complete login.')
                return redirect('core:admin_verify_otp')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
                return render(request, 'core/login.html')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'core/login.html')

def admin_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:admin_login')

def admin_verify_otp(request):
    """Verify OTP for admin login"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    # Check if user is in the OTP verification process
    username = request.session.get('pending_admin_username')
    email = request.session.get('pending_admin_email')
    user_id = request.session.get('pending_admin_user_id')
    
    if not username or not email or not user_id:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('core:admin_login')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp_code', '').strip()
        
        if not otp_input or len(otp_input) != 6:
            messages.error(request, 'Please enter a valid 6-digit OTP.')
            return render(request, 'core/admin_verify_otp.html', {
                'email': email
            })
        
        # Verify OTP
        result = verify_otp(email, otp_input, 'email')
        
        if result['success']:
            # OTP verified - login the user
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=user_id)
                login(request, user)
                
                # Clear session data
                del request.session['pending_admin_username']
                del request.session['pending_admin_email']
                del request.session['pending_admin_user_id']
                if 'otp_attempt' in request.session:
                    del request.session['otp_attempt']
                
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'core:home')
                return redirect(next_url)
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('core:admin_login')
        else:
            # Track failed attempts
            attempt = request.session.get('otp_attempt', 0)
            attempt += 1
            request.session['otp_attempt'] = attempt
            
            if attempt >= 5:
                messages.error(request, 'Too many failed attempts. Please login again.')
                # Clear session
                del request.session['pending_admin_username']
                del request.session['pending_admin_email']
                del request.session['pending_admin_user_id']
                del request.session['otp_attempt']
                return redirect('core:admin_login')
            
            messages.error(request, f'{result["message"]} (Attempt {attempt}/5)')
            return render(request, 'core/admin_verify_otp.html', {
                'email': email,
                'attempt': attempt
            })
    
    return render(request, 'core/admin_verify_otp.html', {
        'email': email
    })

def admin_resend_otp(request):
    """Resend OTP for admin login"""
    email = request.session.get('pending_admin_email')
    username = request.session.get('pending_admin_username')
    
    if not email:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('core:admin_login')
    
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('core:admin_login')
    
    # Create new OTP
    otp = create_otp(email=email, otp_type='email', expiry_minutes=5)
    
    # Send OTP
    success = send_otp_email(email, otp.otp_code, user.first_name or user.username)
    
    if success:
        # Reset attempt counter
        request.session['otp_attempt'] = 0
        messages.success(request, 'New OTP sent to your email.')
    else:
        messages.error(request, 'Failed to resend OTP. Please try again.')
    
    return redirect('core:admin_verify_otp')


def debug_sent_emails(request):
    """Development-only view to list sent emails (outbox).

    Accessible only when DEBUG=True. Shows recent SentEmail records so
    you can screenshot/record OTP email delivery during demos.
    """
    if not getattr(settings, 'DEBUG', False):
        return redirect('core:home')

    from .models import SentEmail
    emails = SentEmail.objects.all()[:30]
    return render(request, 'core/debug_sent_emails.html', {'emails': emails})

@login_required
def home(request):
    # Redirect customers to their dashboard
    if 'customer_id' in request.session:
        return redirect('core:customer_dashboard')

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
            return redirect('core:feedback_list')
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
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        customers = customers.filter(
            Q(name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(customer_id__icontains=query) |
            Q(phone__icontains=query)
        )
    
    # Filter by customer type
    customer_type = request.GET.get('type')
    if customer_type:
        customers = customers.filter(customer_type=customer_type)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(customers, 10)  # 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_type': customer_type,
        'customer_types': Customer.CUSTOMER_TYPES
    }
    return render(request, 'core/customers.html', context)

def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:customer_list')
        else:
            print(form.errors)
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
            messages.success(request, f'Customer "{customer.name}" has been updated successfully.')
            return redirect('core:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'core/add_customer.html', {'form': form, 'customer': customer, 'is_edit': True})

# Delete customer
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    return redirect('core:customer_list')

# View customer details
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    bills = customer.bill_set.all()  # All bills of this customer
    
    # Calculate statistics
    total_bills = bills.count()
    paid_bills = bills.filter(paid=True).count()
    total_billed = sum(bill.total_amount for bill in bills) if bills else 0
    
    context = {
        'customer': customer,
        'bills': bills,
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'total_billed': total_billed,
    }
    return render(request, 'core/customer_detail.html', context)

# Generate QR code for customer
def customer_qr_code(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Create QR code data
    qr_data = f"""Customer ID: {customer.customer_id}
Name: {customer.name}
Email: {customer.email}
Phone: {customer.phone or 'N/A'}
Type: {customer.customer_type}
Monthly Rate: Rs{customer.monthly_rate}"""
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Return as HTTP response
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def bill_list(request):
    bills = Bill.objects.all()
    return render(request, 'core/bill_list.html', {'bills': bills})

def add_bill(request):
    customers = Customer.objects.all()
    waste_items = WasteItem.objects.all()
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(Customer, id=customer_id)
        
       
        now = timezone.now()
       # ❗ Prevent duplicate bill
        if Bill.objects.filter(customer=customer, month=now.month, year=now.year).exists():
            messages.error(request, "Bill for this customer for this month already exists.")
            return redirect('core:add_bill')

        total = Decimal('0')
        bill_items_created = False

        with transaction.atomic():
            bill = Bill.objects.create(
                customer=customer,
                total_amount=0,
                paid=False,
                month=now.month,
                year=now.year
            )

            for item in waste_items:
                qty_str = request.POST.get(f'quantity_{item.id}')

                if qty_str:
                    qty = Decimal(qty_str)

                    if qty < 0:
                        bill.delete()  # Clean up the bill
                        messages.error(request, "Quantity cannot be negative.")
                        return redirect('core:add_bill')

                    if qty > 0:
                        BillItem.objects.create(
                            bill=bill,
                            waste_item=item,
                            quantity=qty
                        )
                        total += (item.unit_price or 0) * qty
                        bill_items_created = True

            if not bill_items_created:
                bill.delete()  # Clean up the empty bill
                messages.error(request, "At least one waste item must have quantity greater than zero.")
                return redirect('core:add_bill')

            bill.total_amount = total
            bill.save()

        return redirect('core:bill_list')

    return render(
        request,
        'core/add_bill.html',
        {
            'customers': customers,
            'waste_items': waste_items
        }
    )
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

def mark_bill_paid(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill.paid = True
    bill.save()
    return redirect('core:bill_detail', bill_id=bill.id)

