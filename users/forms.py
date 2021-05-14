from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import Profile


# class UserRegisterForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ('email', 'password1', 'password2')
#

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username',)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
