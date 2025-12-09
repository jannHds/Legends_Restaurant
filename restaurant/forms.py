from django import forms
from .models import MenuItem
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomerUser
from django.core.exceptions import ValidationError

# ---------------------
# Menu Item Form
# ---------------------
class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'is_available']


# ---------------------
# User Update Form
# ---------------------
User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'role', 'salary', 'hired_at']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        # لو مو staff نخلي hired_at فاضي عشان ما يخرب الدنيا
        if role != 'staff':
            cleaned_data['hired_at'] = None

        return cleaned_data
class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=False,   # واحد من الإيميل أو الجوال يكفي
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
        required=False,   # واحد من الإيميل أو الجوال يكفي
        label="Phone",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "input-field",
                "placeholder": "05XXXXXXXX",
                "title": "Phone number used for contact and login. Must be unique.",
            }
        ),
    )

    address = forms.CharField(
        required=True,
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

    class Meta:
        model = User
        # ✅ نرتب ترتيب الحقول كما تريدين: Username → Email → Phone → Address → Passwords
        fields = ("username", "email", "phone", "address", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ترتيب الحقول في الفورم
        self.order_fields(["username", "email", "phone", "address", "password1", "password2"])

        self.fields["username"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Choose a username",
                "title": "Username used to identify your account.",
            }
        )

        # نخفي الملاحظات الافتراضية للباسورد ونحوّلها Tooltip على الحقل نفسه
        self.fields["password1"].help_text = None
        self.fields["password1"].widget.attrs.update({
            "class": "input-field",
            "placeholder": "Enter password",
            "title": (
               "Password Rules:\n"
               "- Must contain at least 8 characters\n"
               "- Cannot be entirely numeric\n"
               "- Cannot be too similar to your name or email\n"
               "- Must not be a common password"
            ),
        })

        self.fields["password2"].help_text = None
        self.fields["password2"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Confirm password",
                "title": "Re-type the same password to confirm.",
            }
        )

    def clean(self):
        """
        نتحقق أن فيه على الأقل (إيميل أو جوال)
        ونتأكد من uniqueness في جدول CustomerUser
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        if not email and not phone:
            raise ValidationError("Please provide at least an email or a phone number.")

        # لو فيه إيميل، تأكد أنه ما تكرر
        if email and CustomerUser.objects.filter(email=email).exists():
            self.add_error("email", "This email is already registered.")

        # لو فيه جوال، تأكد أنه ما تكرر
        if phone and CustomerUser.objects.filter(phone=phone).exists():
            self.add_error("phone", "This phone number is already registered.")

        return cleaned_data

    def save(self, commit=True):
        """
        1) إنشاء User عادي
        2) إنشاء سجل في CustomerUser بنفس البيانات
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")

        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

            CustomerUser.objects.create(
                user=user,
                username=user.username,
                password=user.password,  # hashed
                email=self.cleaned_data.get("email", ""),
                phone=self.cleaned_data.get("phone", ""),
                address=self.cleaned_data["address"],
            )

        return user

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "input-field",
                "placeholder": "Enter your email",
            }
        ),
    )

    phone = forms.CharField(
        required=True,
        label="Phone",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "input-field",
                "placeholder": "05XXXXXXXX",
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
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone", "address", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تنسيق الحقول + الـ tooltips (الشروط تظهر عند الـ hover)
        self.fields["username"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Choose a username",
                "title": "Username used to identify your account.",
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "title": "Email must be valid and unique for each customer.",
            }
        )
        self.fields["phone"].widget.attrs.update(
            {
                "title": "Phone number must be unique for each customer (used for contact/login).",
            }
        )
        self.fields["address"].widget.attrs.update(
            {
                "title": "Enter your delivery address.",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Enter password",
                "title": "Password should be at least 8 characters.",
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
        نتحقق أن الإيميل أو الجوال ما تكرروا في جدول CustomerUser
        (The system shall allow customers to register using a unique email or phone number.)
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        if email and CustomerUser.objects.filter(email=email).exists():
            self.add_error("email", "This email is already registered.")

        if phone and CustomerUser.objects.filter(phone=phone).exists():
            self.add_error("phone", "This phone number is already registered.")

        return cleaned_data

    def save(self, commit=True):
        """
        1) ننشئ User عادي في Django (username + password)
        2) ننشئ سجل في جدول CustomerUser بنفس البيانات
        3) الـ Customer_id يتولد تلقائياً (AutoField)
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        # نضمن أنه Customer عادي
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

            # ننشئ سجل في جدول Customer_User
            CustomerUser.objects.create(
                user=user,
                username=user.username,
                password=user.password,  # hashed password
                email=self.cleaned_data["email"],
                phone=self.cleaned_data["phone"],
                address=self.cleaned_data["address"],
            )

        return user
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "input-field",
            "placeholder": "Enter your email"
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تعديل شكل الحقول عشان يمشي مع الثيم
        self.fields["username"].widget.attrs.update({
            "class": "input-field",
            "placeholder": "Choose a username"
        })
        self.fields["password1"].widget.attrs.update({
            "class": "input-field",
            "placeholder": "Enter password"
        })
        self.fields["password2"].widget.attrs.update({
            "class": "input-field",
            "placeholder": "Confirm password"
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        # هنا نضمن أنه مستخدم عادي (Customer)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user
    

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

