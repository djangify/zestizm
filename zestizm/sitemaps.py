# from django.contrib.sitemaps import Sitemap
# from django.urls import reverse
# from blog.models import Post, Category as blogCategory
# from shop.models import Product, Category
# from django.utils import timezone
# from infopages.models import InfoPage


# class StaticViewSitemap(Sitemap):
#     priority = 0.6
#     changefreq = "monthly"

#     def items(self):
#         return [
#             "core:home",
#             "core:mini-ecommerce",
#             "core:tech_va",
#             "core:pdf_creation",
#             "core:support",
#             "infopages:policy_index",
#             "infopages:docs_index",
#         ]

#     def location(self, item):
#         return reverse(item)


# class InfoPageSitemap(Sitemap):
#     priority = 0.8
#     changefreq = "monthly"

#     def items(self):
#         # Include only published policies and docs
#         return InfoPage.objects.filter(published=True)

#     def lastmod(self, obj):
#         return obj.last_updated

#     def location(self, obj):
#         if obj.page_type == "policy":
#             return reverse("infopages:policy_detail", kwargs={"slug": obj.slug})
#         return reverse("infopages:doc_detail", kwargs={"slug": obj.slug})


# class blogSitemap(Sitemap):
#     priority = 1.0
#     changefreq = "daily"

#     def items(self):
#         return Post.objects.filter(status="published", publish_date__lte=timezone.now())

#     def lastmod(self, obj):
#         return obj.updated

#     def location(self, obj):
#         return reverse("blog:detail", kwargs={"slug": obj.slug})


# class blogCategorySitemap(Sitemap):
#     priority = 0.6
#     changefreq = "weekly"

#     def items(self):
#         return blogCategory.objects.all()

#     def location(self, obj):
#         return reverse("blog:category", kwargs={"slug": obj.slug})


# class ShopSitemap(Sitemap):
#     priority = 0.9
#     changefreq = "weekly"

#     def items(self):
#         return Product.objects.filter(status="publish", is_active=True)

#     def lastmod(self, obj):
#         return obj.updated

#     def location(self, obj):
#         return reverse("shop:product_detail", kwargs={"slug": obj.slug})


# class ShopCategorySitemap(Sitemap):
#     priority = 0.6
#     changefreq = "weekly"

#     def items(self):
#         return Category.objects.all()

#     def location(self, obj):
#         return reverse("shop:category", kwargs={"slug": obj.slug})


# # Combine all sitemaps in a dictionary
# sitemaps = {
#     "static": StaticViewSitemap,
#     "info_pages": InfoPageSitemap,
#     "blog": blogSitemap,
#     "blog_category": blogCategorySitemap,
#     "shop": ShopSitemap,
#     "shop_category": ShopCategorySitemap,
# }
