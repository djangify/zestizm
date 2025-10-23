from django.contrib import admin
from django.urls import path
from django.urls import include

# from django.contrib.sitemaps.views import sitemap
# from .sitemaps import (
#     StaticViewSitemap,
#     BlogSitemap,
#     BlogCategorySitemap,
#     ShopSitemap,
#     ShopCategorySitemap,
# )
from django.conf import settings
from django.conf.urls.static import static

# sitemaps = {
#     "static": StaticViewSitemap,
#     "blog": NewsSitemap,
#     "category": NewsCategorySitemap,
#     "shop": ShopSitemap,
#     "shop_category": ShopCategorySitemap,
# }

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("", include("shop.urls", namespace="shop")),
    path("", include("infopages.urls")),
    path("accounts/", include("accounts.urls")),
    path("blog/", include("blog.urls")),
    # path(
    #     "sitemap.xml",
    #     sitemap,
    #     {"sitemaps": sitemaps},
    #     name="django.contrib.sitemaps.views.sitemap",
    # ),
    path("tinymce/", include("tinymce.urls")),
]

handler404 = "core.views.handler404"
handler500 = "core.views.handler500"
handler403 = "core.views.handler403"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
