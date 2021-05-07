from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import logout

from users.forms import UserCreateForm
from django.contrib.auth.forms import UserCreationForm


class SignUp(CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'


class LogoutView(TemplateView):

    template_name = 'index.html'

    def logout(self, request):
        logout(request)


