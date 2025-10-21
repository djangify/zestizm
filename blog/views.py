from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Category
from django.utils import timezone


def blog_list(request):
    # Get the current page number
    page = request.GET.get("page", "1")  # Default to page 1 if not specified

    # Get all published regular posts (non-featured)
    regular_posts = Post.objects.filter(
        status="published", publish_date__lte=timezone.now(), is_featured=False
    ).select_related("category")

    # Paginate regular posts
    paginator = Paginator(regular_posts, 24)
    regular_posts_page = paginator.get_page(page)

    # Only get featured posts if we're on page 1
    featured_posts = []
    if page == "1" or not page:
        featured_posts = (
            Post.objects.filter(
                status="published", publish_date__lte=timezone.now(), is_featured=True
            )
            .select_related("category")
            .order_by("-publish_date")[:4]
        )  # Limit to 4 featured posts

    context = {
        "featured_posts": featured_posts,
        "posts": regular_posts_page,
        "categories": Category.objects.all(),
        "title": "Blog",
        "meta_description": "Latest blog and updates from Zestizm",
    }
    return render(request, "blog/list.html", context)


def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category, status="published", publish_date__lte=timezone.now()
    ).order_by("-publish_date")  # Add explicit ordering

    paginator = Paginator(posts, 36)
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    context = {
        "category": category,
        "posts": posts,
        "categories": Category.objects.all(),
        "title": f"{category.name} - blog",
        "meta_description": f"Latest blog and updates about {category.name} from Djangify",
    }

    return render(request, "blog/category.html", context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post, slug=slug, status="published", publish_date__lte=timezone.now()
    )

    # Get next and previous posts
    next_post = (
        Post.objects.filter(
            status="published",
            publish_date__lte=timezone.now(),
            publish_date__gt=post.publish_date,
        )
        .order_by("publish_date")
        .first()
    )

    previous_post = (
        Post.objects.filter(
            status="published",
            publish_date__lte=timezone.now(),
            publish_date__lt=post.publish_date,
        )
        .order_by("-publish_date")
        .first()
    )

    # Get related posts from same category
    related_posts = (
        Post.objects.filter(
            status="published", publish_date__lte=timezone.now(), category=post.category
        )
        .exclude(id=post.id)
        .select_related("category")[:8]
    )

    context = {
        "post": post,
        "next_post": next_post,
        "previous_post": previous_post,
        "related_posts": related_posts,
        "categories": Category.objects.all(),
        "title": post.meta_title or post.title,
        "meta_description": post.get_meta_description,
        "meta_keywords": post.meta_keywords,
        "user": request.user,
    }
    return render(request, "blog/detail.html", context)
