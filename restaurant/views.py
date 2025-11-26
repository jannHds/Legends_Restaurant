from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout


# صفحة رئيسية بسيطة (تقدرين تغيرينها لاحقاً)
def home(request):
    return render(request, "restaurant/base.html")


# ========== AUTHENTICATION ==========

def login_view(request):
    """
    Login مشترك لكل الأدوار:
    Customer / Staff / Manager
    ويحوّل كل واحد للداشبورد الصحيح حسب الـ role.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # RBAC redirect حسب الدور
            if user.role == "customer":
                return redirect("customer_dashboard")
            elif user.role == "staff":
                return redirect("staff_dashboard")
            elif user.role == "manager":
                return redirect("manager_dashboard")
            else:
                # لو فيه role غريب يرجعه للهوم
                return redirect("home")
        else:
            # لاحقاً تقدرين تعرضين الرسالة في الـ template
            return render(
                request,
                "restaurant/login.html",
                {"error": "Invalid username or password"},
            )

    # GET → يعرض صفحة تسجيل الدخول
    return render(request, "restaurant/login.html")


def signup_view(request):
    return render(request, 'restaurant/signup.html')


def logout_view(request):
    logout(request)
    return redirect("login")


# ========== ROLE-BASED DASHBOARDS ==========

def _ensure_role(request, required_role):
    """هيلبر داخلي: يتحقق من تسجيل الدخول والـ role"""
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.role != required_role:
        return HttpResponseForbidden("You are not allowed to access this page.")
    return None


def customer_dashboard(request):
    """
    Customer Dashboard
    """
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    return render(request, "restaurant/customer_dashboard.html")


def staff_dashboard(request):
    """
    Staff Dashboard
    """
    guard = _ensure_role(request, "staff")
    if guard is not None:
        return guard

    return render(request, "restaurant/staff_dashboard.html")


def manager_dashboard(request):
    """
    Manager Dashboard
    """
    guard = _ensure_role(request, "manager")
    if guard is not None:
        return guard

    return render(request, "restaurant/manager_dashboard.html")
