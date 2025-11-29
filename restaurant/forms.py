from django import forms
from .models import MenuItem
from django.contrib.auth import get_user_model

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

