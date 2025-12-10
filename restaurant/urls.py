from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from . import manager_views  # فيه menu_list للمنيو

urlpatterns = [
    # الصفحة الرئيسية
    path("", views.home, name="home"),

    # صفحات الدخول والخروج
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboards حسب الـ role
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("customer/edit/", views.edit_customer_account, name="edit_customer_account"),
    path("customer/signup/", views.customer_signup_view, name="customer_signup"),

    # staff
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path(
        "staff/update/<int:order_id>/<str:new_status>/",
        views.update_order_status,
        name="update_order_status",
    ),

    # manager
    path("manager/dashboard/", views.manager_dashboard, name="manager_dashboard"),

    # زر Manage Users الجديد
    path("manager/users/", views.manage_users, name="manage_users"),
    path("manager/users/<int:user_id>/edit/", views.edit_user_manager, name="edit_user"),
    # زر Manage Menu في صفحة المدير
    path("manager/menu/", manager_views.manager_menu_list, name="manager_menu_list"),
    path("manager/menu/edit/<int:item_id>/", manager_views.edit_menu_item, name="edit_menu_item"),
    path("manager/menu/delete/<int:item_id>/", manager_views.delete_menu_item, name="delete_menu_item"),
    path("manager/menu/toggle/<int:item_id>/", manager_views.toggle_availability, name="toggle_availability"),


    # ✅ صفحة الكارت
    path("cart/", views.cart_view, name="cart_view"),
    
    # ✅ إضافة عنصر إلى الكارت (مستعملة في home.html)
    path("cart/add/<int:item_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:cart_item_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:cart_item_id>/", views.remove_from_cart, name="remove_from_cart"),

    # Checkout + Payment
    path("checkout/", views.checkout_view, name="checkout_view"),
    path("payment/<int:order_id>/", views.payment_process, name="payment_process"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
