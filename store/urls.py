from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('signup/', views.signup, name='signup'),
    path('orders/', views.orders, name='orders'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]
