from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render
from .models import MenuItem

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .forms import CustomerSignUpForm, UserUpdateForm
from .models import Order, OrderItem, MenuItem, Cart, CartItem  # ← أضفنا OrderItem هنا

User = get_user_model()


# ============================
# HOME
# ============================
def home(request):
    """
    صفحة الهوم:
    - تستخدم التمبلت restaurant/home.html
    - تمرر قائمة الأصناف المتاحة من الـ MenuItem إلى الصفحة
    """
    menu_items = MenuItem.objects.filter(is_available=True)
    return render(request, "restaurant/home.html", {"menu_items": menu_items})


# ============================
# AUTHENTICATION
# ============================
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

            role = getattr(user, "role", None)

            if role == "customer":
                return redirect("customer_dashboard")
            elif role == "staff":
                return redirect("staff_dashboard")
            elif role == "manager":
                return redirect("manager_dashboard")
            else:
                return redirect("home")
        else:
            return render(
                request,
                "restaurant/login.html",
                {"error": "Invalid username or password"},
            )

    return render(request, "restaurant/login.html")


def customer_signup_view(request):
    """
    صفحة تسجيل كستمر جديدة باستخدام CustomerSignUpForm
    """
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # تسجيل دخول بعد التسجيل (اختياري)
            login(request, user)
            # غيري "customer_dashboard" لو اسم URL عندكم مختلف
            return redirect("customer_dashboard")
    else:
        form = CustomerSignUpForm()

    context = {
        "form": form,
    }
    return render(request, "restaurant/customer_signup.html", context)


# لو فيه URLs قديمة تشير إلى signup_view، نخليها تعيد استخدام نفس المنطق
def signup_view(request):
    return customer_signup_view(request)


def logout_view(request):
    logout(request)
    return redirect("login")


# ============================
# ROLE-BASED DASHBOARDS
# ============================
def _ensure_role(request, required_role):
    """
    هيلبر داخلي:
    - يتأكد إن المستخدم مسجل دخول
    - ويتأكد إن دوره يطابق الدور المطلوب
    """
    if not request.user.is_authenticated:
        return redirect("login")

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
    """
    Staff Dashboard

    يقرأ الحالات الحقيقية الموجودة في STATUS_CHOICES في الموديل:
    - preparing
    - out_for_delivery
    - delivered
    """
    guard = _ensure_role(request, "staff")
    if guard is not None:
        return guard

    preparing_orders = Order.objects.filter(
        status="preparing"
    ).order_by("-created_at")
    out_for_delivery_orders = Order.objects.filter(
        status="out_for_delivery"
    ).order_by("-created_at")
    delivered_orders = Order.objects.filter(
        status="delivered"
    ).order_by("-created_at")

    context = {
        "preparing_orders": preparing_orders,
        "out_for_delivery_orders": out_for_delivery_orders,
        "delivered_orders": delivered_orders,
    }

    return render(request, "restaurant/staff_dashboard.html", context)


@login_required
def update_order_status(request, order_id, new_status):
    """
    تغيير حالة الطلب من صفحة الستاف
    القيم المسموحة:
    - preparing
    - out_for_delivery
    - delivered
    (مطابقة لـ STATUS_CHOICES بالموديل)
    """
    guard = _ensure_role(request, "staff")
    if guard is not None:
        return guard

    order = get_object_or_404(Order, id=order_id)

    allowed_statuses = ["preparing", "out_for_delivery", "delivered"]

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


# ============================
# MANAGER – MANAGE USERS
# ============================
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

        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username already exists.")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if role not in ["manager", "staff"]:
            errors.append("Role must be either 'manager' or 'staff'.")

        if role == "staff" and not salary_str:
            errors.append("Salary is required for staff users.")

        if salary_str:
            try:
                float(salary_str)
            except ValueError:
                errors.append("Salary must be a valid number.")

        if errors:
            form_error = " | ".join(errors)
        else:
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
                    user.salary = salary_str

            user.save()
            form_success = "User created successfully."

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


# تعديل بيانات مستخدم (للـ manager)
def edit_user(request, user_id):
    guard = _ensure_role(request, "manager")
    if guard is not None:
        return guard

    user_obj = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect("manage_users")
    else:
        form = UserUpdateForm(instance=user_obj)

    return render(
        request,
        "restaurant/edit_user.html",
        {
            "form": form,
            "user_obj": user_obj,
        },
    )


# ============================
# CUSTOMER CART / CHECKOUT / PAYMENT  (Leen)
# ============================
def _get_or_create_cart(user):
    """
    ترجع سلة المستخدم أو تنشئ له واحدة إذا ما عنده
    """
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_view(request):
    """
    عرض صفحة السلة للعميل.
    """
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    cart = _get_or_create_cart(request.user)
    cart_items = cart.cartitem_set.select_related("item")
    cart_total = sum(item.total_price() for item in cart_items)

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "cart_total": cart_total,
    }
    return render(request, "restaurant/cart.html", context)




@login_required
def add_to_cart(request, item_id):
    """
    إضافة صنف من المنيو إلى السلة.
    """
    # يتأكد إن اليوزر Customer
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    # لو ما عندكم is_available احذفيها من الفلتر
    menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    # menu_item = get_object_or_404(MenuItem, id=item_id)  # ← استخدمي هذا لو ما تبين is_available

    cart = _get_or_create_cart(request.user)

    if request.method == "POST":
        # نتأكد إن الكمية رقم صحيح وما هي أقل من 1
        try:
            qty = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            qty = 1

        if qty < 1:
            qty = 1

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item=menu_item,
            defaults={"quantity": qty},
        )

        if not created:
            cart_item.quantity += qty
            cart_item.save()

        messages.success(request, f"{menu_item.name} added to cart.")

    # في كل الحالات نرجع للكارت
    return redirect("cart_view")



@login_required
def update_cart(request, cart_item_id):
    """
    تحديث كمية عنصر داخل السلة.
    إذا صارت الكمية 0 أو أقل، نحذف العنصر.
    """
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        cart__user=request.user,
    )

    if request.method == "POST":
        new_qty = int(request.POST.get("quantity", 1))
        if new_qty <= 0:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")
        else:
            cart_item.quantity = new_qty
            cart_item.save()
            messages.success(request, "Cart updated.")

    return redirect("cart_view")


@login_required
def remove_from_cart(request, cart_item_id):
    """
    حذف عنصر من السلة مباشرة.
    """
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        cart__user=request.user,
    )
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect("cart_view")


@login_required
@transaction.atomic
def checkout_view(request):
    """
    صفحة التأكيد قبل إنشاء الطلب الفعلي.
    """
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    cart = _get_or_create_cart(request.user)
    cart_items = cart.cartitem_set.select_related("item")

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart_view")

    cart_total = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            total=cart_total,
            status="preparing",    # نفس اللي في STATUS_CHOICES بالموديل
            order_type="takeaway",  # تقدرين تغيرينها لاحقاً حسب اختيار اليوزر
        )

        for c_item in cart_items:
            OrderItem.objects.create(
                order=order,
                item=c_item.item,
                quantity=c_item.quantity,
                price=c_item.item.price,
            )

        cart_items.delete()

        messages.success(
            request,
            f"Order #{order.id} created. Proceed to payment.",
        )
        return redirect("payment_process", order_id=order.id)

    context = {
        "cart_items": cart_items,
        "cart_total": cart_total,
    }
    return render(request, "restaurant/checkout.html", context)


@login_required
def payment_process(request, order_id):
    """
    محاكاة عملية الدفع:
    - أول زيارة: زر Pay Now
    - بعد الضغط: نغيّر حالة الطلب إلى delivered
    """
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    if request.method == "POST":
        # ما عندنا بوابة دفع حقيقية، بس نحاكي نجاح الدفع
        order.status = "delivered"   # موجودة في STATUS_CHOICES
        order.save()

        messages.success(
            request,
            f"Payment successful for Order #{order.id}.",
        )
        return render(
            request,
            "restaurant/payment.html",
            {"order": order, "paid": True},
        )

    return render(
        request,
        "restaurant/payment.html",
        {"order": order, "paid": False},
    )
@login_required
@login_required
def cart_view(request):
    """
    عرض صفحة السلة للعميل.
    """
    guard = _ensure_role(request, "customer")
    if guard is not None:
        return guard

    cart = _get_or_create_cart(request.user)

    # نستخدم related_name="items"
    cart_items = cart.items.select_related("item")

    # نستفيد من دالة Cart.total_price()
    cart_total = cart.total_price()

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "cart_total": cart_total,
    }
    return render(request, "restaurant/cart.html", context)






