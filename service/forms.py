from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(help_text='Required')
    first_name = forms.CharField(max_length=50, help_text='Required')
    last_name = forms.CharField(max_length=50, help_text='Required')

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

