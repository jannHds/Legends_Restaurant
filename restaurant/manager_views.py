from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import MenuItem
from .forms import MenuItemForm

# ------------------------------
# Manager Dashboard
# ------------------------------
def manager_dashboard(request):
    categories_count = MenuItem.CATEGORY_CHOICES.__len__()
    today_orders_count = 0  # (بنعدلها لاحقاً إذا سوّيتوا order system)

    context = {
        "categories_count": categories_count,
        "today_orders_count": today_orders_count,
    }

    return render(request, "restaurant/manager_dashboard.html", context)



# التحقق أن المستخدم مدير
def is_manager(user):
    return user.is_authenticated and user.role == "manager"


# ================================
#  قائمة المينيو
# ================================
@user_passes_test(is_manager)
def manager_menu_list(request):
    items = MenuItem.objects.all().order_by("category")

    # إضافة عنصر جديد
    if request.method == "POST" and "add_item" in request.POST:
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("menu_list")
    else:
        form = MenuItemForm()

    return render(request, "restaurant/manager_menu_list.html", {
        "menu_items": items,
        "form": form
    })


# ================================
#  تعديل عنصر
# ================================
@user_passes_test(is_manager)
def edit_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("menu_list")

    return redirect("menu_list")


# ================================
#  حذف عنصر
# ================================
@user_passes_test(is_manager)
def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    return redirect("menu_list")


# ================================
#  توفر العنصر (On/Off)
# ================================
@user_passes_test(is_manager)
def toggle_availability(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.is_available = not item.is_available
    item.save()
    return redirect("menu_list")





