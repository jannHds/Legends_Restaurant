from django.urls import path
from . import views
from . import manager_views  # فيه menu_list للمنيو
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # الصفحة الرئيسية
    path("", views.home, name="home"),

    # صفحات الدخول والخروج
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboards حسب الـ role
    path("customer/dashboard/", views.customer_dashboard,
         name="customer_dashboard"),
    #staff
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/update/<int:order_id>/<str:new_status>/", views.update_order_status, name="update_order_status"),

    path("manager/dashboard/", views.manager_dashboard, name="manager_dashboard"),
    

    # زر Manage Menu في صفحة المدير
    path("manager/menu/", manager_views.manager_menu_list, name="manager_menu_list"),

    # زر Manage Users الجديد
    path("manager/users/", views.manage_users, name="manage_users"),
    path('manager/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),

    path("customer/signup/", views.customer_signup_view, name="customer_signup"),


    path('manager/menu/', manager_views.menu_list, name='menu_list'),
    path('manager/menu/add/', manager_views.add_menu_item, name='add_menu_item'),
    path('manager/menu/edit/<int:item_id>/', manager_views.edit_menu_item, name='edit_menu_item'),
    path('manager/menu/delete/<int:item_id>/', manager_views.delete_menu_item, name='delete_menu_item'),
    path('manager/menu/toggle/<int:item_id>/', manager_views.toggle_availability, name='toggle_availability'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

