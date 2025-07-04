# core/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from users.models import Goal, SubCategory
# Get the active User model
User = get_user_model()


class LoginForm(AuthenticationForm):
    """
    A custom login form that inherits from Django's AuthenticationForm.
    This allows us to easily customize the fields' appearance and placeholders.
    """
    username = forms.CharField(
        label="Foydalanuvchi nomi",
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'Email yoki foydalanuvchi nomingiz'
        })
    )
    password = forms.CharField(
        label="Parol",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Parolingizni kiriting'
        })
    )

class RegistrationForm(forms.Form):
    """
    A form for user registration.
    It includes fields for first name, email, and password confirmation.
    """
    first_name = forms.CharField(
        label="Ism",
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Masalan, John'})
    )
    email = forms.EmailField(
        label="Elektron pochta",
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'sizning@pochta.com'})
    )
    password = forms.CharField(
        label="Parol", 
        widget=forms.PasswordInput, 
        required=True
    )
    password2 = forms.CharField(
        label="Parolni tasdiqlang", 
        widget=forms.PasswordInput, 
        required=True
    )

    def clean_email(self):
        """
        Validates that the email address is not already in use.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ushbu elektron pochta manzili allaqachon ro'yxatdan o'tgan.")
        return email

    def clean(self):
        """
        Verifies that the two password fields match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password and password2 and password != password2:
            self.add_error('password2', "Parollar bir-biriga mos kelmadi.")
        return cleaned_data

class GoalForm(forms.ModelForm):
    """
    An advanced form for creating and updating a Goal instance,
    matching the new design.
    """
    duration = forms.ChoiceField(
        choices=Goal.DURATION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'hidden'}),
        label="Davomiyligi"
    )

    class Meta:
        model = Goal
        fields = [
            'title', 'description', 'category', 'sub_category', 'duration', 
            'visibility', 'phone_number', 'telegram_username'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Maqsad nomi'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Izoh qoldirish'}),
            'visibility': forms.Select(),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Telefon raqam kiritish'}),
            'telegram_username': forms.TextInput(attrs={'placeholder': 'Telegram user kiritish'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Yo'nalish tanlang"
        self.fields['sub_category'].empty_label = "Ichki yo'nalish"
        self.fields['sub_category'].queryset = SubCategory.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['sub_category'].queryset = self.instance.category.subcategories.order_by('name')
