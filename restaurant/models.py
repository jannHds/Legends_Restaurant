from django.db import models
from django.contrib.auth.models import AbstractUser
# لاحظي: شلنا import User من django.contrib.auth.models
# لأننا نستخدم اليوزر المخصص اللي تحت


# ============================
# CUSTOM USER
# ============================
class User(AbstractUser):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("staff", "Staff"),
        ("manager", "Manager"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer",
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # معلومات إضافية للستاف
    hired_at = models.DateTimeField(blank=True, null=True)
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )

    def is_customer(self):
        return self.role == "customer"

    def is_staff_user(self):
        return self.role == "staff"

    def is_manager(self):
        return self.role == "manager"

    def _str_(self):
        return self.username


# ============================
# MENU ITEM
# ============================
class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ("drinks", "Drinks"),
        ("main", "Main Dishes"),
        ("appetizers", "Appetizers"),
        ("sweet", "Sweet"),
        ("special", "Special Dishes"),
    ]

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(
        upload_to="menu_images/",
        blank=True,
        null=True,
    )
    is_available = models.BooleanField(default=True)

    def _str_(self):
        return self.name


# ============================
# CART (سلة العميل)
# ============================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        # نستخدم related_name="items" من CartItem
        items = self.items.all()
        # CartItem.total_price عندك @property → بدون أقواس
        return sum(item.total_price for item in items)

    def _str_(self):
        return f"{self.user.username}'s Cart"




# ============================
# CART ITEM (عنصر داخل السلة)
# ============================
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.item.price * self.quantity

    def _str_(self):
        return f"{self.quantity} × {self.item.name}"


# ============================
# ORDER
# ============================
class Order(models.Model):
    STATUS_CHOICES = [
        ("preparing", "Preparing"),
        ("out_for_delivery", "Out For Delivery"),
        ("delivered", "Delivered"),
    ]

    TYPE_CHOICES = [
        ("takeaway", "Takeaway"),
        ("delivery", "Delivery"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="preparing",
    )
    order_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default="takeaway",
    )
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # مهم للكود حق الدفع:
    is_paid = models.BooleanField(default=False)

    def _str_(self):
        return f"Order #{self.id} - {self.user.username}"


# ============================
# ORDER ITEM
# ============================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def total(self):
        return self.price * self.quantity

    def _str_(self):
        return f"{self.quantity} × {self.item.name}"


# ============================
# CUSTOMER USER (اختياري)
# ============================
class CustomerUser(models.Model):
    # هذا هو Customer_id = INT(PK) ويتولد تلقائياً
    customer_id = models.AutoField(primary_key=True)

    # نخزن الربط مع User الأساسي (اختياري لكن مفيد جداً)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        null=True,
        blank=True,
    )

    username = models.CharField(max_length=150)
    # ملاحظة: عادة ما نخزن الباسورد هنا، يكفي User نفسه
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255)

    def _str_(self):
        return f"{self.username} ({self.customer_id})"