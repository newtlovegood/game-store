from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [

    path('single/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('user/<int:id>/', views.UserOrderView.as_view(), name='order-user'),
    path('current/', views.UserCurrentOrderView.as_view(), name='order-current'),
    path('all/', views.AllOrdersView.as_view(), name='order-all'),
    path('add-to-cart/<pk>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', views.remove_from_cart, name='remove-from-cart'),
    path('checkout/', views.OrderCheckoutView.as_view(), name='checkout'),
]

