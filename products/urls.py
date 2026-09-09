from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('enquiry/', views.enquiry_view, name='enquiry'),
    path('enquiry/success/<int:enquiry_id>/', views.enquiry_success_view, name='enquiry_success'),
]
