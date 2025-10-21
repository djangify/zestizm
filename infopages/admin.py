from django.contrib import admin
from .models import InfoPage


@admin.register(InfoPage)
class InfoPageAdmin(admin.ModelAdmin):
    list_display = ("title", "page_type", "published", "last_updated")
    list_filter = ("page_type", "published")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("page_type", "title")

    fieldsets = (
        (None, {"fields": ("title", "slug", "page_type", "published")}),
        ("Content", {"fields": ("content",)}),
        ("Meta", {"fields": ("last_updated",)}),
    )
    readonly_fields = ("last_updated",)
