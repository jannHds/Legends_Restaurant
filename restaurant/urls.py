from django.urls import path
from . import views

urlpatterns = [
    # الصفحة الرئيسية /
    path("", views.home, name="home"),

    # صفحات الدخول والخروج
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboards حسب الـ RBAC
    path("customer/dashboard/", views.customer_dashboard,
         name="customer_dashboard"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("manager/dashboard/", views.manager_dashboard, name="manager_dashboard"),
]
