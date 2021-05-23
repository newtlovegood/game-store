from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [

    path('single/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('user/<int:id>/', views.UserOrderView.as_view(), name='order-user'),
    path('current/', views.UserCurrentOrderView.as_view(), name='order-current'),
    path('all/', views.AllOrdersView.as_view(), name='order-all'),
    path('add-to-cart/', views.add_to_basket, name='add-to-cart'),
    path('increment-to-cart/', views.increment_to_basket, name='increment-to-cart'),
    path('remove-from-cart/', views.remove_from_basket, name='remove-from-cart'),
    path('reduce-in-cart/', views.reduce_from_basket, name='reduce-in-cart'),
    path('checkout/', views.OrderCheckoutView.as_view(), name='checkout'),
]

