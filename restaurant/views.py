from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .forms import CustomerSignUpForm
from .models import Order
from django.contrib.auth.decorators import login_required


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
            # يسجّل الدخول فعلياً
            login(request, user)

            # نجيب الـ role بأمان (لو ما عنده role ما يطيح البرنامج)
            role = getattr(user, "role", None)

            if role == "customer":
                return redirect("customer_dashboard")
            elif role == "staff":
                return redirect("staff_dashboard")
            elif role == "manager":
                return redirect("manager_dashboard")
            else:
                # لو ما فيه role أو شيء مو متوقّع
                return redirect("home")
        else:
            # لو اليوزر/الباس غلط → نرجع لنفس صفحة اللوق إن مع رسالة
            return render(
                request,
                "restaurant/login.html",
                {"error": "Invalid username or password"},
            )

    # GET → أول مرة يفتح الصفحة
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

    # لو الدور مختلف، نعرض صفحة شكلها حلو بدل النص العادي
    if getattr(request.user, "role", None) != required_role:
        return render(
            request,
            "restaurant/access_denied.html",
            {"required_role": required_role},
            status=403,
        )

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
    pending_orders = Order.objects.filter(status="Pending").order_by("-created_at")
    preparing_orders = Order.objects.filter(status="Preparing").order_by("-created_at")
    ready_orders = Order.objects.filter(status="Ready").order_by("-created_at")

    context = {
        "pending_orders": pending_orders,
        "preparing_orders": preparing_orders,
        "ready_orders": ready_orders,
    }
    guard = _ensure_role(request, "staff")
    if guard is not None:
        return guard

    return render(request, "restaurant/staff_dashboard.html", context)

@login_required
def update_order_status(request, order_id, new_status):
   
    guard = _ensure_role(request, "staff")
    if guard is not None:
        return guard

    order = get_object_or_404(Order, id=order_id)

    allowed_statuses = ["Pending", "Preparing", "Ready", "Completed"]

    if new_status not in allowed_statuses:
        return HttpResponseForbidden("Invalid status")

    order.status = new_status
    order.save()

    return redirect("staff_dashboard")


def manager_dashboard(request):
    """
    Manager Dashboard
    """
    guard = _ensure_role(request, "manager")
    if guard is not None:
        return guard

    return render(request, "restaurant/manager_dashboard.html")


User = get_user_model()


def manage_users(request):
    """
    صفحة المدير لإدارة المستخدمين (manager / staff)
    - تضيف مستخدم جديد مع phone, address, salary
    - تضبط hired_at تلقائياً إذا كان role = staff
    - تعرض جدول المستخدمين مع فلتر حسب الدور
    """
    guard = _ensure_role(request, "manager")
    if guard is not None:
        return guard

    form_error = None
    form_success = None

    # فلتر الدور في الجدول (GET parameter)
    role_filter = request.GET.get("role", "all")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        role = request.POST.get("role")
        password = (request.POST.get("password") or "").strip()

        phone = (request.POST.get("phone") or "").strip()
        address = (request.POST.get("address") or "").strip()
        salary_str = (request.POST.get("salary") or "").strip()

        errors = []

        # فحوصات أساسية
        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username already exists.")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if role not in ["manager", "staff"]:
            errors.append("Role must be either 'manager' or 'staff'.")

        # لو ستاف لازم نكتب الراتب
        if role == "staff" and not salary_str:
            errors.append("Salary is required for staff users.")

        # لو فيه راتب تأكدي أنه رقم
        if salary_str:
            try:
                float(salary_str)
            except ValueError:
                errors.append("Salary must be a valid number.")

        if errors:
            form_error = " | ".join(errors)
        else:
            # إنشاء المستخدم
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            user.role = role
            user.phone = phone
            user.address = address

            if role == "staff":
                user.hired_at = timezone.now()
                if salary_str:
                    user.salary = salary_str  # Django يحولها تلقائياً لـ DecimalField

            user.save()
            form_success = "User created successfully."

    # تجهيز قائمة المستخدمين مع الفلتر
    users_qs = User.objects.filter(role__in=["manager", "staff"])

    if role_filter in ["manager", "staff"]:
        users_qs = users_qs.filter(role=role_filter)

    users = users_qs.order_by("username")

    return render(
        request,
        "restaurant/manage_users.html",
        {
            "users": users,
            "form_error": form_error,
            "form_success": form_success,
            "role_filter": role_filter,
        },
    )
# restaurant/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import UserUpdateForm
from django.contrib.auth import get_user_model

User = get_user_model()

def edit_user(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect('manage_users')  # اسم URL صفحة المانجر اللي فيها الجدول
    else:
        form = UserUpdateForm(instance=user_obj)

    context = {
        'form': form,
        'user_obj': user_obj,
    }
    return render(request, 'manager/edit_user.html', context)
def edit_user(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = UserUpdateForm(instance=user_obj)

    return render(request, 'restaurant/edit_user.html', {
        'form': form,
        'user_obj': user_obj,
    })
def customer_signup_view(request):
    """
    Customer Sign Up Page
    """
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # تسجيل الدخول مباشرة بعد التسجيل (تقدرين تشيلينه لو ما تبغينه)
            login(request, user)
            # غيري "customer_home" لاسم الـ URL الخاص بداشبورد الكستمر عندكم
            return redirect("customer_home")  # مثال: "customer_dashboard"
    else:
        form = CustomerSignUpForm()

    context = {
        "form": form,
    }
    return render(request, "restaurant/customer_signup.html", context)

