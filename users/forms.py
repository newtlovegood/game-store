from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import models


class UserCreateForm(UserCreationForm):

    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Display Name'
        self.fields['email'].label = 'Email Address'

