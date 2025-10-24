from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

# --- Import models ---
# Blog models (for blog section)
from blog.models import Post, Category as BlogCategory

# Shop models (for product listings)
from shop.models import Product, Category as ProductCategory

# --- Forms ---
from .forms import SupportForm


def home(request):
    """
    Homepage for Djangify.
    Displays hero section, featured products, latest products,
    and recent blog posts — all with correct ProductCategory filtering.
    """

    # -------------------------------
    # 1. Product Query
    # -------------------------------
    base_products = Product.objects.filter(
        is_active=True, status__in=["publish", "soon", "full"]
    ).order_by("-created")

    # --- Handle category filter (ProductCategory only) ---
    category_slug = request.GET.get("category")
    current_category = None
    if category_slug:
        current_category = get_object_or_404(ProductCategory, slug=category_slug)
        base_products = base_products.filter(category=current_category)

    # --- Handle search query ---
    query = request.GET.get("q", "").strip()
    if query:
        base_products = base_products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # -------------------------------
    # 2. Product Sections
    # -------------------------------
    categories = ProductCategory.objects.all()

    # Latest 4 products
    latest_products = base_products[:4]
    latest_ids = latest_products.values_list("id", flat=True)

    # Featured products (2 max)
    featured_products = Product.objects.filter(
        featured=True, is_active=True, status="publish"
    ).order_by("order", "-created")[:2]
    featured_ids = featured_products.values_list("id", flat=True)

    # Additional products (remaining)
    additional_products = (
        base_products.exclude(id__in=latest_ids)
        .exclude(id__in=featured_ids)
        .order_by("-created")
    )

    # Optional pagination for the additional section
    paginator = Paginator(additional_products, 8)
    page = request.GET.get("page")
    products_page = paginator.get_page(page)

    # -------------------------------
    # 3. Blog Posts (from BlogCategory)
    # -------------------------------
    blog_posts = (
        Post.objects.filter(status="published", publish_date__lte=timezone.now())
        .select_related("category")
        .order_by("-publish_date")[:3]
    )

    # -------------------------------
    # 4. Context
    # -------------------------------
    context = {
        "categories": categories,  # product categories for pills
        "current_category": current_category,  # active filter
        "latest_products": latest_products,
        "featured_products": featured_products,
        "additional_products": products_page,
        "blog_posts": blog_posts,
        "query": query,  # search term
    }

    return render(request, "core/home.html", context)


def handler500(request):
    return render(request, "error/500.html", status=500)


def handler403(request, exception):
    return render(request, "error/403.html", status=403)


def handler404(request, exception):
    # Define which category to show (by slug)
    category_slug = "tech-va"  # Change this to your desired category slug

    try:
        # Try to get the category
        category = get_object_or_404(BlogCategory, slug=category_slug)

        # Get posts from the category
        category_posts = Post.objects.filter(
            category=category, status="published", publish_date__lte=timezone.now()
        ).order_by("-publish_date")[:4]

    except Http404:
        # Fallback to recent posts if category doesn't exist
        category_posts = Post.objects.filter(
            status="published", publish_date__lte=timezone.now()
        ).order_by("-publish_date")[:3]
        category = None

    context = {"category_posts": category_posts, "selected_category": category}

    return render(request, "error/404.html", context, status=404)


def support(request):
    form = SupportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()  # saves to DB + emails + auto-ack
        messages.success(request, "Thank you! Your message has been sent.")
        return redirect("core:support")
    return render(request, "core/support.html", {"form": form})


@require_GET
def robots_txt(request):
    """
    robots.txt for Zestizm.com
    Optimised for search engines and AI answer engines.
    """

    lines = [
        # --- AI and LLM Crawlers: explicitly allowed ---
        "User-agent: GPTBot",
        "Disallow:",
        "User-agent: PerplexityBot",
        "Disallow:",
        "User-agent: ClaudeBot",
        "Disallow:",
        "User-agent: Google-Extended",  # used by Bard / Gemini
        "Disallow:",
        "User-agent: ChatGPT-User",
        "Disallow:",
        # --- All other crawlers ---
        "User-agent: *",
        # Block sensitive or duplicate areas
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /login/",
        "Disallow: /logout/",
        "Disallow: /register/",
        "Disallow: /dashboard/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        "Disallow: /orders/",
        "Disallow: /media/private/",
        # Allow key public content
        "Allow: /",
        "Allow: /shop/",
        "Allow: /blog/",
        "Allow: /policies/",
        "Allow: /docs/",
        "Allow: /support/",
        # Sitemap reference
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        "#",
        "# Zestizm – Age-Positive Zest For Life",
        "# Helping women rediscover their zest for life with small, science-backed actions.",
        "# Learn more at https://www.zestizm.com",
        "#",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
