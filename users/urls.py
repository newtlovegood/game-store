from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='games:home'), name='logout'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
]