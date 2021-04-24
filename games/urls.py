from django.urls import path
from . import views

app_name = 'games'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('games/<int:pk>/', views.SingleGameView.as_view(), name='detail'),
    path('games/add/', views.GameCreateView.as_view(), name='add'),
    path('games/<int:pk>/update/', views.GameEditView.as_view(), name='edit'),
    path('games/<int:pk>/delete/', views.GameDeleteView.as_view(), name='delete'),
]



