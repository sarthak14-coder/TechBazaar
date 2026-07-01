from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Avg
from datetime import date, timedelta

from .models import (
    Product,
    Cart,
    Order,
    Wishlist,
    Rating,
    Review,
)


# ---------------- HOME ----------------

def home(request):
    query = request.GET.get("q")

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return render(request, "store/home.html", {
        "products": products,
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
    })


# ---------------- CART ----------------

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Product added to cart successfully!")

    return redirect("home")


@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    total_price = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "total_price": total_price,
    })


@login_required
def remove_from_cart(request, cart_id):
    item = Cart.objects.get(
        id=cart_id,
        user=request.user
    )

    item.delete()

    messages.success(request, "Product removed from cart.")

    return redirect("cart")

    # ---------------- PRODUCT DETAIL ----------------

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)

    average_rating = Rating.objects.filter(
        product=product
    ).aggregate(Avg("rating"))["rating__avg"]

    reviews = Review.objects.filter(
        product=product
    ).order_by("-created_at")

    return render(request, "store/product_detail.html", {
        "product": product,
        "average_rating": average_rating,
        "reviews": reviews,
    })


# ---------------- CHECKOUT ----------------

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    total_price = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    delivery_date = date.today() + timedelta(days=5)

    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "delivery_date": delivery_date,
    })


# ---------------- PLACE ORDER ----------------

@login_required
def place_order(request):

    if request.method == "POST":

        payment = request.POST.get("payment")
        upi_id = request.POST.get("upi_id")

        if payment in ["Google Pay", "Paytm"] and not upi_id:
            messages.error(request, "Please enter your UPI ID.")
            return redirect("checkout")

        cart_items = Cart.objects.filter(user=request.user)

        total_price = sum(
            item.product.price * item.quantity
            for item in cart_items
        )

        delivery_date = date.today() + timedelta(days=5)

        product_names = ", ".join(
            f"{item.product.name} (x{item.quantity})"
            for item in cart_items
        )

        Order.objects.create(
            user=request.user,
            full_name=request.POST["full_name"],
            phone=request.POST["phone"],
            address=request.POST["address"],
            city=request.POST["city"],
            pincode=request.POST["pincode"],
            payment_method=payment,
            product_name=product_names,
            total_price=total_price,
            delivery_date=delivery_date,
        )

        cart_items.delete()

        return render(request, "store/order_success.html")

    return redirect("checkout")

# ---------------- SIGNUP ----------------

def signup(request):

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {
        "form": form
    })


# ---------------- ORDERS ----------------

@login_required
def orders(request):

    user_orders = Order.objects.filter(
        user=request.user
    ).order_by("-order_date")

    return render(request, "store/orders.html", {
        "orders": user_orders
    })


# ---------------- STATIC PAGES ----------------

def contact(request):
    return render(request, "store/contact.html")


def about(request):
    return render(request, "store/about.html")

# ---------------- PRODUCT RATING ----------------

@login_required
def rate_product(request, product_id):

    product = Product.objects.get(id=product_id)

    rating_value = request.POST.get("rating")

    Rating.objects.update_or_create(
        user=request.user,
        product=product,
        defaults={
            "rating": rating_value
        }
    )

    messages.success(request, "Thanks for rating this product ⭐")

    return redirect("product_detail", product_id=product.id)


# ---------------- WISHLIST ----------------

@login_required
def add_to_wishlist(request, product_id):

    product = Product.objects.get(id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    messages.success(request, "Product added to Wishlist ❤️")

    return redirect("home")


@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    )

    return render(request, "store/wishlist.html", {
        "wishlist_items": wishlist_items
    })


@login_required
def remove_from_wishlist(request, wishlist_id):

    item = Wishlist.objects.get(
        id=wishlist_id,
        user=request.user
    )

    item.delete()

    messages.success(request, "Product removed from Wishlist.")

    return redirect("wishlist")


# ---------------- REVIEW ----------------

@login_required
def add_review(request, product_id):

    product = Product.objects.get(id=product_id)

    if request.method == "POST":

        comment = request.POST.get("comment")

        if comment:

            Review.objects.create(
                user=request.user,
                product=product,
                comment=comment
            )

            messages.success(request, "Review added successfully.")

    return redirect("product_detail", product_id=product.id)

    # ---------------- INVOICE ----------------

@login_required
def invoice(request, order_id):

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    html = render_to_string(
        "store/invoice.html",
        {
            "order": order
        }
    )

    return HttpResponse(html)