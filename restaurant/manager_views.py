from django.shortcuts import render, redirect, get_object_or_404
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


# ------------------------------
# Menu List (view items)
# ------------------------------
def menu_list(request):
    items = MenuItem.objects.all()
    return render(request, "restaurant/menu_list.html", {"items": items})


# ------------------------------
# Create Menu Item
# ------------------------------
def menu_create(request):
    if request.method == "POST":
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("manager_menu_list")
    else:
        form = MenuItemForm()

    return render(request, "restaurant/menu_form.html", {"form": form})


# ------------------------------
# Update Menu Item
# ------------------------------
def menu_update(request, id):
    item = get_object_or_404(MenuItem, id=id)

    if request.method == "POST":
        form = MenuItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("manager_menu_list")
    else:
        form = MenuItemForm(instance=item)

    return render(request, "restaurant/menu_form.html", {"form": form})


# ------------------------------
# Delete Menu Item
# ------------------------------
def menu_delete(request, id):
    item = get_object_or_404(MenuItem, id=id)
    item.delete()
    return redirect("manager_menu_list") 

from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

def user_list(request):
    # لاحقاً بنصمم صفحه مرتبة
    users = User.objects.all()
    return render(request, "restaurant/manager_user_list.html", {"users": users})
