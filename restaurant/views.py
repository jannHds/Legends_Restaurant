from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .forms import CustomerSignUpForm
from .models import Order
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order, MenuItem
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import UserUpdateForm
from django.contrib.auth import get_user_model
from .forms import UserUpdateForm, CustomerAccountForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
                return redirect("home")
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



@login_required
def customer_dashboard(request):
    
    # لازم يكون مسجل دخول
    if not request.user.is_authenticated:
        return redirect("login")

    # لو دخل ستاف → نرجعه لصفحة الستاف
    if request.user.role == "staff":
        return redirect("staff_dashboard")

    # لو دخل مانجر → نرجعه لصفحة المانجر
    if request.user.role == "manager":
        return redirect("manager_dashboard")
    user = request.user

    # 1) إجمالي الطلبات
    total_orders = Order.objects.filter(user=user).count()

    # 2) حالة آخر طلب
    last_order = Order.objects.filter(user=user).order_by('-created_at').first()

    last_status = None
    if last_order:
        last_status = last_order.get_status_display()  # يخليها "Preparing" بدل preparing

    # 3) الطلبات حسب الحالة
    preparing = Order.objects.filter(user=user, status='preparing').count()
    out_for_delivery = Order.objects.filter(user=user, status='out_for_delivery').count()
    delivered = Order.objects.filter(user=user, status='delivered').count()

    # 4) توصيات (نختار 3 أكلات عشوائية من المينيو)
    recommendations = MenuItem.objects.filter(is_available=True).order_by('?')[:3]

    # 5) أبرز المينيو (نختار 4 عناصر عشوائية)
    highlights = MenuItem.objects.filter(is_available=True).order_by('?')[:4]

    context = {
        "username": user.username,
        "total_orders": total_orders,
        "last_order": last_order,
        "last_status": last_status,

        "preparing": preparing,
        "out_for_delivery": out_for_delivery,
        "delivered": delivered,

        "recommendations": recommendations,
        "highlights": highlights,
    }

    return render(request, "restaurant/customer_dashboard.html", context)
    """
    Simple Customer Home page after login
    """
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    return render(request, "restaurant/customer_home.html")



@login_required
def staff_dashboard(request):

    pending = Order.objects.filter(status="Pending")
    confirmed = Order.objects.filter(status="Confirmed")
    preparing = Order.objects.filter(status="Preparing")
    ready = Order.objects.filter(status="Ready")
    completed_today = Order.objects.filter(status="Delivered")

    context = {
        "pending": pending,
        "confirmed": confirmed,
        "preparing": preparing,
        "ready": ready,
        "completed_today": completed_today,
    }

    return render(request, "restaurant/staff_dashboard.html", context)



@login_required
def update_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id)
    
    valid_flow = {
        "Pending": ["Confirmed", "Rejected"],
        "Confirmed": ["Preparing"],
        "Preparing": ["Ready"],
        "Ready": ["Delivered"],
    }

    if new_status in valid_flow.get(order.status, []):
        order.status = new_status
        order.save()
        messages.success(request, f"Order {order_id} updated to {new_status}")
    else:
        messages.error(request, "Invalid status transition")

    return render(request, "restaurant/staff_dashboard.html")


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'restaurant/order_detail.html', {'order': order})





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

        users_qs = User.objects.filter(role__in=["manager", "staff", "customer"])
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
    users_qs = User.objects.filter(role__in=["manager", "staff", "customer"])

    if role_filter in ["manager", "staff", "customer"]:
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
User = get_user_model()

def edit_user_manager(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect('manage_users')
    else:
        form = UserUpdateForm(instance=user_obj)

    return render(request, 'manager/edit_user.html', {
        'form': form,
        'user_obj': user_obj,
    })

@login_required
def edit_customer_account(request):
    user_obj = request.user  # الكستمر يعدّل نفسه فقط

    if request.method == "POST":
        form = CustomerAccountForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Account updated successfully.")
            return redirect("customer_dashboard")
    else:
        form = CustomerAccountForm(instance=user_obj)

    return render(request, "restaurant/customer_account_edit.html", {
        "form": form,
        "user_obj": user_obj,
    })

def customer_signup_view(request):
    """
    Customer Sign Up Page (for role = customer)
    Uses CustomerSignUpForm to create a new user, then logs them in
    and redirects to the customer dashboard.
    """
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            # form.save() يفترض أنه ينشئ User مع role = "customer"
            user = form.save()
            login(request, user)
            # حاليًا عندكم customer_dashboard شغّال، لذلك نوجّه له
            return redirect("home")
    else:
        form = CustomerSignUpForm()

    context = {
        "form": form,
    }
    # هذا التمبلت هو اللي Jana راح تشتغل عليه
    return render(request, "restaurant/customer_signup.html", context)

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

