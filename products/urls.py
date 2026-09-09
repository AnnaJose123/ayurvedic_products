from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('enquiry/', views.enquiry_view, name='enquiry'),
    path('enquiry/success/<int:enquiry_id>/', views.enquiry_success_view, name='enquiry_success'),
    
    # Customer Authentication & Dashboard Routes
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-enquiries/', views.my_enquiries_view, name='my_enquiries'),
]

