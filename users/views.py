from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth import logout

from order.models import Order
from django.contrib.auth.forms import UserCreationForm

#
# class ProfileUpdate(UpdateView):
#
#
