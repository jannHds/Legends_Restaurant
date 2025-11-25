from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")

            if request.user.role != required_role:
                return HttpResponseForbidden("You are not allowed to access this page.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def customer_required(view):
    return role_required("customer")(view)


def staff_required(view):
    return role_required("staff")(view)


def manager_required(view):
    return role_required("manager")(view)
