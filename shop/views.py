# shop/views.py
from .models import Category, Product, Order, OrderItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, Http404
from django.views.decorators.http import require_POST, require_http_methods
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import stripe
import os
import logging
from django.db.models import Q
import mimetypes
from wsgiref.util import FileWrapper
from shop.forms import GuestDetailsForm, ProductReviewForm
from .emails import send_order_confirmation_email, send_download_link_email
from .cart import Cart


stripe.api_key = settings.STRIPE_SECRET_KEY

# Set up logger
logger = logging.getLogger("shop")


def product_list(request, template_name="core/home.html"):
    """
    Main product listing view.
    Displays 4 latest products at the top (by publish date)
    and excludes them from the main 8-product paginated grid below.
    """
    categories = Category.objects.all()
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category")

    # Base queryset
    base_products = Product.objects.filter(
        is_active=True, status__in=["publish", "soon", "full"]
    ).order_by("-created")

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        base_products = base_products.filter(category=current_category)

    if query:
        base_products = base_products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Top 4 latest products
    latest_products = base_products[:4]
    latest_ids = latest_products.values_list("id", flat=True)

    # Exclude those from bottom section
    remaining_products = base_products.exclude(id__in=latest_ids)

    # Paginate the remaining products (8 per page)
    paginator = Paginator(remaining_products, 8)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    # Featured products (limit 2)
    featured_products = Product.objects.filter(
        featured=True, is_active=True, status="publish"
    ).order_by("order", "-created")[:2]

    return render(
        request,
        template_name,
        {
            "latest_products": latest_products,
            "products": products,
            "categories": categories,
            "current_category": current_category,
            "stripe_publishable_key": getattr(settings, "STRIPE_PUBLISHABLE_KEY", ""),
            "query": query,
            "featured_products": featured_products,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product, slug=slug, is_active=True, status__in=["publish", "soon", "full"]
    )

    related_products = Product.objects.filter(
        category=product.category,
        status__in=["publish", "full"],
        is_active=True,
    ).exclude(id=product.id)[:3]

    has_purchased = False
    order_item = None
    review_form = None

    if request.user.is_authenticated:
        order_item = OrderItem.objects.filter(
            order__user=request.user, order__paid=True, product=product
        ).first()

        has_purchased = bool(order_item)
        review_form = ProductReviewForm() if product.can_review(request.user) else None

    # fetch additional images
    images = product.images.all()

    return render(
        request,
        "shop/detail.html",
        {
            "product": product,
            "related_products": related_products,
            "has_purchased": has_purchased,
            "order_item": order_item,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "form": review_form,
            "images": images,
            "request": request,
        },
    )


@require_POST
def cart_add(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get("quantity", 1))
        cart.add(product=product, quantity=quantity)
        messages.success(request, f"{product.title} has been added to your cart.")
        return redirect("shop:cart_detail")
    except Exception as e:
        messages.error(request, "There was an error adding the item to your cart.")
        return redirect("core:home")


def category_hub(request):
    categories = Category.objects.all()
    return render(request, "shop/category_hub.html", {"categories": categories})


def cart_detail(request):
    try:
        cart = Cart(request)
        return render(request, "shop/cart.html", {"cart": cart})
    except Exception as e:
        print(f"Error in cart detail: {str(e)}")
        messages.error(request, "There was an error displaying your cart.")
        return redirect("core:home")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("shop:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(product=product, quantity=quantity, override_quantity=True)
    return redirect("shop:cart_detail")


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:cart_detail")

    guest_form = None
    if not request.user.is_authenticated:
        if request.method == "POST":
            guest_form = GuestDetailsForm(request.POST)
            if guest_form.is_valid():
                request.session["guest_details"] = {
                    "first_name": guest_form.cleaned_data["first_name"],
                    "last_name": guest_form.cleaned_data["last_name"],
                    "email": guest_form.cleaned_data["email"],
                    "phone": guest_form.cleaned_data["phone"],
                }
            else:
                return HttpResponseBadRequest("Invalid form data")
        else:
            guest_form = GuestDetailsForm()

    try:
        total_price = cart.get_total_price()

        if total_price <= 0:
            messages.error(request, "Invalid cart total")
            return redirect("shop:cart_detail")

        # Create a new PaymentIntent each time user loads checkout
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Stripe works in pence/cents
            currency=getattr(settings, "STRIPE_CURRENCY", "gbp"),
            payment_method_types=["card"],
            metadata={
                "user_id": str(request.user.id)
                if request.user.is_authenticated
                else "guest",
                "is_guest": str(not request.user.is_authenticated),
            },
            receipt_email=(
                request.user.email
                if request.user.is_authenticated
                else request.session.get("guest_details", {}).get("email")
            ),
        )

        context = {
            "client_secret": intent.client_secret,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "cart": cart,
            "guest_form": guest_form,
            "is_guest": not request.user.is_authenticated,
            "payment_intent_id": intent.id,
        }
        return render(request, "shop/checkout.html", context)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during checkout: {str(e)}")
        messages.error(request, f"Payment processing error: {str(e)}")
        return redirect("shop:cart_detail")

    except Exception as e:
        logger.error(f"Unexpected checkout error: {str(e)}")
        messages.error(request, "An error occurred during checkout. Please try again.")
        return redirect("shop:cart_detail")


def payment_success(request):
    payment_intent_id = request.GET.get("payment_intent")
    if not payment_intent_id:
        messages.error(request, "No payment information found.")
        return redirect("shop:cart_detail")

    try:
        # Verify payment with Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if payment_intent.status != "succeeded":
            logger.warning(f"Payment intent {payment_intent_id} not succeeded")
            messages.error(request, "Payment was not successful.")
            return redirect("shop:cart_detail")

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to complete checkout.")
            return redirect("accounts:login")

        email = request.user.email

        # Prevent duplicate order creation on refresh
        existing_order = Order.objects.filter(
            payment_intent_id=payment_intent_id
        ).first()
        if existing_order:
            return redirect("shop:purchases")

        cart = Cart(request)

        # Create order
        order = Order.objects.create(
            user=request.user,
            email=email,
            payment_intent_id=payment_intent_id,
            paid=True,
            status="completed",
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price_paid_pence=int(item["price"] * 100),
                quantity=item["quantity"],
                downloads_remaining=item["product"].download_limit,
            )

            product = item["product"]
            product.purchase_count += item["quantity"]
            product.save()

        try:
            send_order_confirmation_email(order)
        except Exception as e:
            logger.error(f"Failed to send order confirmation email: {str(e)}")

        cart.clear()

        return render(request, "shop/success.html", {"order": order})

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        messages.error(request, f"Error: {str(e)}")
        return redirect("shop:cart_detail")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        messages.error(request, "There was an error processing your order.")
        return redirect("shop:cart_detail")


def payment_cancel(request):
    messages.error(request, "Payment was cancelled.")
    return redirect("shop:cart_detail")


@login_required
def download_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order_item = OrderItem.objects.filter(
        order__user=request.user, product=product
    ).first()

    if not order_item:
        messages.error(request, "You have not purchased this product.")
        return redirect("shop:product_detail", slug=product.slug)

    if order_item.download_count >= settings.MAX_DOWNLOAD_LIMIT:
        messages.error(request, "You have reached the download limit for this product.")
        return redirect("shop:purchases")

    # Increment download count
    order_item.download_count += 1
    order_item.save()

    # Send download link email
    try:
        context = {
            "order_item": order_item,
            "product": order_item.product,
            "site_url": settings.SITE_URL,
            "downloads_remaining": order_item.downloads_remaining,
            "user": order_item.order.user,
            "email": (
                order_item.order.user.email
                if order_item.order.user
                else order_item.order.guest_details.email
            ),
            "unsubscribe_url": f"{settings.SITE_URL}/profiles/email-preferences/",
        }
        send_download_link_email(order_item, context)
    except Exception as e:
        logger.error(
            f"Failed to send download email for order item {order_item.id}: {str(e)}"
        )

    # Get download URL
    download_url = product.get_download_url()
    if not download_url:
        messages.error(request, "Download URL not available.")
        return redirect("shop:purchases")

    return redirect(download_url)


@login_required
def purchases(request):
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "shop/purchases.html", {"orders": orders})


def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category, status__in=["publish", "soon", "full"], is_active=True
    ).order_by("order", "-created")
    categories = Category.objects.all()

    paginator = Paginator(products, 20)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    return render(
        request,
        "core/home.html",
        {
            "products": products,
            "categories": categories,
            "current_category": category,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "shop/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "shop/purchases.html", {"order": order})


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Something failed: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Something failed: {str(e)}")
        return HttpResponse(status=400)

    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        handle_successful_payment(payment_intent)
    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        handle_failed_payment(payment_intent)

    return HttpResponse(status=200)


def handle_successful_payment(payment_intent):
    order = Order.objects.filter(payment_intent_id=payment_intent.id).first()
    if order and not order.paid:
        order.paid = True
        order.status = "completed"
        order.save()

        try:
            for order_item in order.items.all():
                send_download_link_email(order_item)
        except Exception as e:
            print(f"Error sending download emails in webhook: {str(e)}")

        try:
            send_order_confirmation_email(order)
        except Exception as e:
            print(f"Error sending order confirmation email: {str(e)}")


def handle_failed_payment(payment_intent):
    order = Order.objects.filter(payment_intent_id=payment_intent.id).first()
    if order:
        order.status = "failed"
        order.save()


@login_required
@require_http_methods(["GET"])
def secure_download(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Check if the order item belongs to the user
    if order_item.order.user != request.user:
        raise PermissionDenied

    # Check download limits for digital products only
    if order_item.product.product_type == "download":
        if order_item.download_count >= order_item.downloads_remaining:
            messages.error(
                request, "You have reached your download limit for this product."
            )
            return redirect("accounts:profile")

        # Decrement downloads_remaining and increment download_count
        order_item.downloads_remaining -= 1
        order_item.download_count += 1
        order_item.save()

    # Get the file path
    file_path = None
    if order_item.product.files:
        file_path = order_item.product.files.path

    if not file_path or not os.path.exists(file_path):
        raise Http404("File not found")

    # Get the file's mime type
    content_type, encoding = mimetypes.guess_type(file_path)
    content_type = content_type or "application/octet-stream"

    # Open the file
    file_obj = open(file_path, "rb")
    response = FileResponse(FileWrapper(file_obj), content_type=content_type)
    response["Content-Disposition"] = (
        f'attachment; filename="{os.path.basename(file_path)}"'
    )
    return response


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Allow superusers to review without purchase verification
    if not request.user.is_superuser:
        if not product.can_review(request.user):
            messages.error(request, "You can only review products you have purchased.")
            return redirect("shop:product_detail", slug=product.slug)

    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.verified_purchase = True
            review.save()
            messages.success(request, "Your review has been added.")
            return redirect("shop:product_detail", slug=product.slug)
    else:
        form = ProductReviewForm()

    return render(request, "shop/add_review.html", {"form": form, "product": product})
