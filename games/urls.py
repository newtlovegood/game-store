from django.urls import path
from . import views

app_name = 'games'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('<uuid:pk>/', views.SingleGameView.as_view(), name='detail'),
    path('add/', views.GameCreateView.as_view(), name='add'),
    path('update/<uuid:pk>/', views.GameEditView.as_view(), name='edit'),
    path('delete/<uuid:pk>/', views.GameDeleteView.as_view(), name='delete'),
    path('filter/', views.GameFilterView.as_view(), name='filter'),
    path('filter/<pk>/', views.GameFilterView.as_view(), name='filter'),
    path('search/', views.GameSearchView.as_view(), name='search'),
]



