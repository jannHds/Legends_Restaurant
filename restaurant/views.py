from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
SAR = "﷼"

def home(request):
    return render(request, 'restaurant/customer_dashboard.html')

def customer_dashboard(request):
    context = {
        "username": "Customer",
        "pending_orders": 2,
        "last_order_status": "Preparing",
        "recommendations": ["Margherita Pizza", "Chicken Wrap", "Iced Latte"],
        "SAR": SAR,
    }
    return render(request, 'restaurant/customer_dashboard.html', context)

def staff_dashboard(request):
    context = {
        "username": "Staff",
        "new_orders": 5,
        "in_progress": 3,
        "ready_for_pickup": 2,
        "SAR": SAR,
    }
    return render(request, 'restaurant/staff_dashboard.html', context)

def manager_dashboard(request):
    context = {
        "username": "Manager",
        "today_revenue": 1240.5,
        "orders_today": 27,
        "low_stock_items": ["Tomatoes", "Burger Buns"],
        "SAR": SAR,
    }
    return render(request, 'restaurant/manager_dashboard.html', context)
