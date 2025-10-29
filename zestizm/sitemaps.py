from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from blog.models import Post, Category as BlogCategory
from shop.models import Product, Category as ShopCategory
from infopages.models import InfoPage


# --- Static pages ---
class StaticViewSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        # Add zest-for-life so it appears in the sitemap
        return [
            "core:home",
            "core:support",
            "core:zest_for_life",
        ]

    def priority(self, item):
        if item == "core:home":
            return 1.0
        if item == "core:zest_for_life":
            return 1.0
        if item == "core:support":
            return 0.3

    def location(self, item):
        return reverse(item)

    def get_metadata(self, item):
        if item == "core:home":
            return {
                "title": "Zestizm – Age-Positive Energy & Confidence",
                "description": (
                    "Zestizm helps women reignite their zest for life with "
                    "simple, science-backed tools for emotional flexibility and vitality."
                ),
                "keywords": "age positive, zest for life, midlife confidence, emotional flexibility, small joys",
            }

        if item == "core:support":
            return {
                "title": "Support – Zestizm Help & Contact",
                "description": "Get in touch with Zestizm for product support, questions, or account help.",
                "keywords": "zestizm support, customer help, contact",
            }

        if item == "core:zest_for_life":
            return {
                "title": "Zest for Life – A Practical Guide to Everyday Aliveness",
                "description": (
                    "Discover how to rebuild your zest for life with daily sparks of presence, movement, "
                    "and reflection. A grounded, age-positive guide to feeling alive again."
                ),
                "keywords": "zest for life, aliveness, emotional energy, daily sparks, age positive, zestizm",
            }


# --- Info pages ---
class InfoPageSitemap(Sitemap):
    priority = 0.4
    changefreq = "monthly"

    def items(self):
        return InfoPage.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.last_updated

    def location(self, obj):
        if obj.page_type == "policy":
            return reverse("infopages:policy_detail", kwargs={"slug": obj.slug})
        return reverse("infopages:doc_detail", kwargs={"slug": obj.slug})


# --- Blog posts and categories ---
class BlogPostSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Post.objects.filter(status="published", publish_date__lte=timezone.now())

    def lastmod(self, obj):
        return obj.updated

    def location(self, obj):
        return reverse("blog:detail", kwargs={"slug": obj.slug})

    def get_metadata(self, obj):
        return {
            "title": obj.get_meta_title,
            "description": obj.get_meta_description,
            "keywords": obj.meta_keywords
            or "age positive blog, zest, vitality, emotional flexibility",
        }


class BlogCategorySitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return BlogCategory.objects.all()

    def location(self, obj):
        return reverse("blog:category", kwargs={"slug": obj.slug})


# --- Shop products and categories ---
class ShopProductSitemap(Sitemap):
    priority = 0.95
    changefreq = "daily"

    def items(self):
        return Product.objects.filter(status="publish", is_active=True)

    def lastmod(self, obj):
        return obj.updated

    def location(self, obj):
        return reverse("shop:product_detail", kwargs={"slug": obj.slug})

    def get_metadata(self, obj):
        return {
            "title": f"{obj.title} – Zestizm",
            "description": (
                f"{obj.title}: {obj.description[:150]}... "
                "The Age-Positive Zestizm range. Return to a zest for life. Reignite zest in the life you already have."
            ),
            "keywords": "age postivity, age positive, zest for life, zest sparks, mini guide, emotional flexibility, small joys, zestizm",
        }


class ShopCategorySitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return ShopCategory.objects.all()

    def location(self, obj):
        return reverse("shop:category", kwargs={"slug": obj.slug})


# --- Register all sitemaps ---
sitemaps = {
    "static": StaticViewSitemap,
    "info_pages": InfoPageSitemap,
    "blog": BlogPostSitemap,
    "blog_category": BlogCategorySitemap,
    "shop": ShopProductSitemap,
    "shop_category": ShopCategorySitemap,
}
