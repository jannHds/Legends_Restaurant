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
    يستخدم في صفحة Manage Employees لتعديل بيانات المستخدم
    (username, email, phone, address, role, salary, hired_at)
    """

    class Meta:
        model = User
        fields = ["username", "email", "phone", "address", "role", "salary", "hired_at"]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        # لو مو staff نخلي hired_at فاضي عشان ما يخرب الدنيا
        if role != "staff":
            cleaned_data["hired_at"] = None

        return cleaned_data


# ==========================
# 3) Customer SignUp Form
# ==========================
class CustomerSignUpForm(UserCreationForm):
    """
    Customer Sign Up Form:
    - ينشئ User في جدول المستخدمين
    - يضبط role = "customer" (لو الحقل موجود)
    - ينشئ سجل في CustomerUser مربوط بنفس الـ User
    - يسمح بالتسجيل باستخدام إيميل أو جوال أو الاثنين (واحد منهم على الأقل)
    """

    email = forms.EmailField(
        required=False,  # واحد من الإيميل أو الجوال يكفي
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
        required=False,  # واحد من الإيميل أو الجوال يكفي
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

    # العنوان غير إجباري بناءً على طلبك
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
        # الترتيب: Username → Email → Phone → Address → Passwords
        fields = ("username", "email", "phone", "address", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ترتيب الحقول في الفورم
        self.order_fields(["username", "email", "phone", "address", "password1", "password2"])

        # شكل وترتيب الحقول
        self.fields["username"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Choose a username",
                "title": "Username used to identify your account.",
            }
        )

        # نخفي الملاحظات الافتراضية للباسورد ونحوّلها Tooltip على الحقل نفسه
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
        """
        نتأكد أن فيه على الأقل (إيميل أو جوال)
        ونتأكد من uniqueness في جدول CustomerUser
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        # واحد منهم لازم يكون موجود
        if not email and not phone:
            raise ValidationError("Please provide at least an email or a phone number.")

        # لو فيه إيميل، تأكد أنه غير مكرر
        if email and CustomerUser.objects.filter(email=email).exists():
            self.add_error("email", "This email is already registered.")

        # لو فيه جوال، تأكد أنه غير مكرر
        if phone and CustomerUser.objects.filter(phone=phone).exists():
            self.add_error("phone", "This phone number is already registered.")

        return cleaned_data

    def save(self, commit=True):
        """
        1) إنشاء User (في جدول المستخدمين الرئيسي)
        2) تعيين role = "customer" (لو حقل role موجود في User)
        3) إنشاء سجل في CustomerUser مربوط بنفس الـ User
        """
        user = super().save(commit=False)

        # تخزين الإيميل (وباقي البيانات لو الحقول موجودة في User model)
        user.email = self.cleaned_data.get("email", "")

        if hasattr(user, "phone"):
            user.phone = self.cleaned_data.get("phone", "")

        if hasattr(user, "address"):
            user.address = self.cleaned_data.get("address", "")

        # ربطه كـ Customer للنظام لو فيه حقل role
        if hasattr(user, "role"):
            user.role = "customer"

        # نتأكد أنه مو staff ولا superuser
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

            # ننشئ سجل في جدول CustomerUser
            CustomerUser.objects.create(
                user=user,
                username=user.username,
                password=user.password,  # hashed
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

        # تنسيق بسيط للحقول مع ثيم Legends
        for field in self.fields.values():
            field.widget.attrs.update({"class": "lr-input"})
