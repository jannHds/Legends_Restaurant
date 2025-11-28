from django.urls import path
from . import views
from . import manager_views    # CRUD for manager menu

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

    # --------------------------
    # Manager Menu CRUD
    # --------------------------
    path("manager/menu/", manager_views.menu_list, name="manager_menu_list"),
    path("manager/menu/add/", manager_views.menu_create, name="manager_menu_add"),
    path("manager/menu/edit/<int:id>/", manager_views.menu_update, name="manager_menu_edit"),
    path("manager/menu/delete/<int:id>/", manager_views.menu_delete, name="manager_menu_delete"),
    # ========== MANAGER: User Management ==========

    path("manager/users/", manager_views.user_list, name="manager_user_list"),

]
