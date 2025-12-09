from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import MenuItem
from .forms import MenuItemForm


# -----------------------------------
# التحقق أن المستخدم مدير فقط
# -----------------------------------
def is_manager(user):
    return user.is_authenticated and user.role == "manager"


# -----------------------------------
# صفحة إدارة المنيو (عرض + إضافة)
# -----------------------------------
@user_passes_test(is_manager)
def manager_menu_list(request):

    menu_items = MenuItem.objects.all().order_by("category")

    # إضافة عنصر جديد
    if request.method == "POST" and "add_item" in request.POST:
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("manager_menu_list")
    else:
        form = MenuItemForm()

    return render(request, "restaurant/manager_menu_list.html", {
        "menu_items": menu_items,   # ← الاسم الصحيح المتوافق مع التمبليت
        "form": form,
    })


# -----------------------------------
# تعديل عنصر
# -----------------------------------
@user_passes_test(is_manager)
def edit_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("manager_menu_list")
    else:
        form = MenuItemForm(instance=item)

    return render(request, "restaurant/partials/edit_form_fields.html", {"form": form})



# -----------------------------------
# حذف عنصر
# -----------------------------------
@user_passes_test(is_manager)
def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    return redirect("manager_menu_list")


# -----------------------------------
# تغيير حالة توفر العنصر (Available / Unavailable)
# -----------------------------------
@user_passes_test(is_manager)
def toggle_availability(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.is_available = not item.is_available
    item.save()
    return redirect("manager_menu_list")






