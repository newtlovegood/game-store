from django.urls import path
from . import views

app_name = 'games'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('<int:pk>/', views.SingleGameView.as_view(), name='detail'),
    path('add/', views.GameCreateView.as_view(), name='add'),
    path('<int:pk>/update/', views.GameEditView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.GameDeleteView.as_view(), name='delete'),
    path('genre/<slug:slug>/', views.GameFilterView.as_view(), name='filter'),
    path('search/', views.GameSearchView.as_view(), name='search'),
]



