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
    path("shop/", include(("shop.urls", "shop"), namespace="shop")),
    path("blog/", include(("blog.urls", "blog"), namespace="blog")),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("tinymce/", include("tinymce.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", core_views.robots_txt, name="robots_txt"),
    path("", include("infopages.urls")),  # this is okay because it uses specific slugs
    path("", include(("core.urls", "core"), namespace="core")),
]

# --- Error Handlers ---
handler404 = "core.views.handler404"
handler500 = "core.views.handler500"
handler403 = "core.views.handler403"

# --- Static / Media (Dev only) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin customization
admin.site.site_header = "Zestizm"
admin.site.site_title = "Zestizm"
admin.site.index_title = "Welcome to Your Site"
