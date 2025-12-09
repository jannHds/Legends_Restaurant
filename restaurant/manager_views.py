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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import MenuItem
from .forms import MenuItemForm

# التحقق أن المستخدم مدير فقط
def is_manager(user):
    return user.is_authenticated and user.role == "manager"


@user_passes_test(is_manager)
def menu_list(request):
    items = MenuItem.objects.all()
    return render(request, 'restaurant/menu_list.html', {'items': items})

@user_passes_test(is_manager)
def add_menu_item(request):
    if request.method == "POST":
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menu_list')
    else:
        form = MenuItemForm()

    return render(request, 'restaurant/add_menu_item.html', {'form': form})


@user_passes_test(is_manager)
def edit_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    if request.method == "POST":
        form = MenuItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('menu_list')
    else:
        form = MenuItemForm(instance=item)

    return render(request, 'restaurant/edit_menu_item.html', {'form': form, 'item': item})


@user_passes_test(is_manager)
def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    return redirect('menu_list')


@user_passes_test(is_manager)
def toggle_availability(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.is_available = not item.is_available
    item.save()
    return redirect('menu_list')



def menu_list(request):
    menu_items = MenuItem.objects.all().order_by('category')

    # إضافة عنصر جديد
    if request.method == "POST" and "add_item" in request.POST:
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("menu_list")
    else:
        form = MenuItemForm()

    context = {
        "menu_items": menu_items,
        "form": form,
    }
    return render(request, "restaurant/manager_menu_list.html", context)


def edit_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("menu_list")
    return redirect("menu_list")


def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    return redirect("menu_list")


def toggle_availability(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.is_available = not item.is_available
    item.save()
    return redirect("menu_list")




