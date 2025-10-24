from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from core import views as core_views
from .sitemaps import sitemaps

urlpatterns = [
    path("admin/", admin.site.urls),
    # --- Core / Home ---
    path("", include(("core.urls", "core"), namespace="core")),
    path("shop/", include(("shop.urls", "shop"), namespace="shop")),
    path("blog/", include(("blog.urls", "blog"), namespace="blog")),
    # --- Info Pages (Policies + Docs) ---
    path("policies/", include("infopages.urls")),
    path("docs/", include("infopages.urls")),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("tinymce/", include("tinymce.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", core_views.robots_txt, name="robots_txt"),
]

# --- Error Handlers ---
handler404 = "core.views.handler404"
handler500 = "core.views.handler500"
handler403 = "core.views.handler403"

# --- Static / Media (Dev only) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
