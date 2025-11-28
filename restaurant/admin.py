from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, MenuItem, Cart, CartItem, Order, OrderItem


# === Custom User Admin to show "role" inside Django admin ===
class CustomUserAdmin(UserAdmin):
    # نضيف الحقل داخل صفحة التفاصيل
    fieldsets = UserAdmin.fieldsets + (
        ("Role Information", {"fields": ("role",)}),
    )

    # نضيف الحقل داخل صفحة إنشاء مستخدم جديد
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role Information", {"fields": ("role",)}),
    )


# === Register models ===
admin.site.register(User, CustomUserAdmin)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

