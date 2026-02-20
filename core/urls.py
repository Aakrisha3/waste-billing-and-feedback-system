from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('verify-otp/', views.admin_verify_otp, name='admin_verify_otp'),
    path('resend-otp/', views.admin_resend_otp, name='admin_resend_otp'),
    # Development-only debug outbox
    path('debug/sent-emails/', views.debug_sent_emails, name='debug_sent_emails'),

    # Home
    path('', views.home, name='home'),

    # Feedback
    path('feedbacks/', views.feedback_list, name='feedback_list'),
    path('feedbacks/add/', views.add_feedback, name='add_feedback'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/qr/', views.customer_qr_code, name='customer_qr_code'),

    

    # Bills
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/add/', views.add_bill, name='add_bill'),
    path('bills/<int:bill_id>/', views.bill_detail, name='bill_detail'),
    path('bills/<int:bill_id>/edit/', views.edit_bill, name='edit_bill'),
    path('bills/<int:bill_id>/delete/', views.delete_bill, name='delete_bill'),
    path('bills/<int:bill_id>/mark_paid/', views.mark_bill_paid, name='mark_bill_paid'),

    


]
