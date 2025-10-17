from django.urls import path
from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
]

