from django.shortcuts import render
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Product, Cart, Order, Wishlist
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import views
from .models import Wishlist

def home(request):
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'store/home.html', {
        'products': products
    })

from .models import Product, Cart
from django.shortcuts import redirect

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, "Product added to cart successfully!")
    return redirect('home')

def cart(request):
    cart_items = Cart.objects.all()

    total_price = 0

    for item in cart_items:
        total_price += item.product.price * item.quantity

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def remove_from_cart(request, cart_id):
    item = Cart.objects.get(id=cart_id)
    item.delete()
    return redirect('cart')

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)

    return render(request, 'store/product_detail.html', {
        'product': product
    })    

from datetime import date, timedelta
@login_required
def checkout(request):
    cart_items = Cart.objects.all()

    total_price = 0

    for item in cart_items:
        total_price += item.product.price * item.quantity

    delivery_date = date.today() + timedelta(days=5)

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'delivery_date': delivery_date
    })
def home(request):
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'store/home.html', {
        'products': products
    })    

@login_required
def place_order(request):
    if request.method == "POST":

        cart_items = Cart.objects.all()

        total_price = 0

        for item in cart_items:
            total_price += item.product.price * item.quantity

        delivery_date = date.today() + timedelta(days=5)

        product_names = ", ".join(
            [f"{item.product.name} (x{item.quantity})" for item in cart_items]
        )

        Order.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            city=request.POST['city'],
            pincode=request.POST['pincode'],
            payment_method=request.POST['payment'],
            product_name=product_names,
            total_price=total_price,
            delivery_date=delivery_date
        )

        cart_items.delete()

        return render(request, 'store/order_success.html')

    return redirect('checkout')



def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})    

@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user)

    return render(request, 'store/orders.html', {
        'orders': user_orders
    })

def contact(request):
    return render(request, 'store/contact.html')

def about(request):
    return render(request, 'store/about.html')

@login_required
def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    messages.success(request, "Product added to Wishlist ❤️")

    return redirect('home')


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)

    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def remove_from_wishlist(request, wishlist_id):
    item = Wishlist.objects.get(id=wishlist_id, user=request.user)
    item.delete()

    return redirect('wishlist')
