from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import MenuItem, CustomerUser

# نستخدم الـ User المخصص في المشروع
User = get_user_model()


# ==========================
# 1) Menu Item Form
# ==========================
class MenuItemForm(forms.ModelForm):
    """
    Form لإدارة عناصر المنيو في لوحة الموظف/المدير.
    - يدعم رفع صورة للطبق (image)
    - يستخدم كلاس CSS: lr-input / lr-textarea
    """

    class Meta:
        model = MenuItem
        fields = ["name", "description", "price", "category", "image", "is_available"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "lr-input"}),
            "description": forms.Textarea(
                attrs={"class": "lr-textarea", "rows": 2}
            ),
            "price": forms.NumberInput(attrs={"class": "lr-input"}),
            "category": forms.Select(attrs={"class": "lr-input"}),
            "image": forms.ClearableFileInput(attrs={"class": "lr-input"}),
            "is_available": forms.CheckboxInput(attrs={"class": "lr-input"}),
        }


# ==========================
# 2) User Update Form (للموظفين/المدير)
# ==========================
class UserUpdateForm(forms.ModelForm):
    """
    يستخدم في صفحة Manage Employees لتعديل بيانات المستخدم:
    (username, email, phone, address, role, salary, hired_at)
    """

    class Meta:
        model = User
        fields = ["username", "email", "phone", "address", "role", "salary", "hired_at"]

    def clean_salary(self):
        """
        نضمن أن salary إما رقم صحيح (Decimal) أو None
        (ما يكون سترنق فاضي أو قيمة غريبة تسبب decimal.InvalidOperation)
        """
        salary = self.cleaned_data.get("salary")

        # لو تركته فاضي أو None → نخليه None عشان يتخزن NULL في الداتابيس
        if salary in ("", None):
            return None

        return salary

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        # لو مو staff نخلي hired_at فاضي
        if role != "staff":
            cleaned_data["hired_at"] = None

        return cleaned_data


# ==========================
# 3) Customer SignUp Form
# ==========================
class CustomerSignUpForm(UserCreationForm):
    """
    فورم تسجيل عميل جديد
    - واحد من (email أو phone) على الأقل
    - address اختياري
    """

    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "input-field",
                "placeholder": "Enter your email",
                "title": "Provide a valid email. It will be used for account recovery and notifications.",
            }
        ),
    )

    phone = forms.CharField(
        required=False,
        label="Phone",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "input-field",
                "placeholder": "05XXXXXXXX",
                "title": "Phone number used for contact/login. Must be unique.",
            }
        ),
    )

    address = forms.CharField(
        required=False,
        label="Address",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "input-field",
                "placeholder": "Enter your address",
                "title": "Enter your delivery address.",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone", "address", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.order_fields(["username", "email", "phone", "address", "password1", "password2"])

        self.fields["username"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Choose a username",
                "title": "Username used to identify your account.",
            }
        )

        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

        self.fields["password1"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Enter password",
                "title": (
                    "Password Rules:\n"
                    "- Must contain at least 8 characters\n"
                    "- Cannot be entirely numeric\n"
                    "- Cannot be too similar to your name or email\n"
                    "- Must not be a common password"
                ),
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Confirm password",
                "title": "Re-type the same password to confirm.",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        if not email and not phone:
            raise ValidationError("Please provide at least an email or a phone number.")

        if email and CustomerUser.objects.filter(email=email).exists():
            self.add_error("email", "This email is already registered.")

        if phone and CustomerUser.objects.filter(phone=phone).exists():
            self.add_error("phone", "This phone number is already registered.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data.get("email", "")
        if hasattr(user, "phone"):
            user.phone = self.cleaned_data.get("phone", "")
        if hasattr(user, "address"):
            user.address = self.cleaned_data.get("address", "")

        if hasattr(user, "role"):
            user.role = "customer"

        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

            CustomerUser.objects.create(
                user=user,
                username=user.username,
                password=user.password,
                email=self.cleaned_data.get("email", ""),
                phone=self.cleaned_data.get("phone", ""),
                address=self.cleaned_data.get("address", ""),
            )

        return user


# ==========================
# 4) Customer Account Form (تعديل حساب العميل)
# ==========================
class CustomerAccountForm(forms.ModelForm):
    """
    يستخدم في صفحة "My Account" للعميل
    لتعديل: username, email, phone, address
    """

    class Meta:
        model = User
        fields = ["username", "email", "phone", "address"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "lr-input"})
