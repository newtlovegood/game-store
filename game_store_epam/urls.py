"""game_store_epam URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from users.views import ProfileUpdate, CustomLogoutView, CustomLoginView
from games.views import HomePageView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('games/', include('games.urls')),
    path('', HomePageView.as_view(), name='home'),
    path('accounts/', include('allauth.urls')),
    path('accounts/login', CustomLoginView.as_view(), name='account_login'),
    path('accounts/logout', CustomLogoutView.as_view(), name='account_logout'),
    path('accounts/profile', ProfileUpdate.as_view(), name='profile'),
    path('order/', include('order.urls')),
    path('comments/', include('comment.urls')),
    path('thanks/', views.ThanksView.as_view(), name='thanks'),

    # below RENDERS media images on local machine
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
