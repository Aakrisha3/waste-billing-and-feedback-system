from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
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

    

    # Bills
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/add/', views.add_bill, name='add_bill'),
    path('bills/<int:bill_id>/', views.bill_detail, name='bill_detail'),
    path('bills/<int:bill_id>/edit/', views.edit_bill, name='edit_bill'),
    path('bills/<int:bill_id>/delete/', views.delete_bill, name='delete_bill'),

    
]
