from django.urls import path
from . import views

app_name = 'games'
urlpatterns = [
    path('', views.HomePageView.as_view()),
    path('games/<int:pk>/', views.SingleGameView.as_view(), name='detail'),
]