from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminTextareaWidget
import requests

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove TinyMCE from ad_code
        if "ad_code" in self.fields:
            self.fields["ad_code"].widget = AdminTextareaWidget(
                attrs={"rows": 6, "class": "vLargeTextField"}
            )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm

    list_display = [
        "title",
        "category",
        "status",
        "is_featured",
        "publish_date",
        "display_thumbnail",
        "has_ad",
    ]
    list_editable = ["is_featured"]
    list_filter = ["status", "category", "is_featured", "created", "publish_date"]
    search_fields = ["title", "content", "meta_title", "meta_description"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "publish_date"
    readonly_fields = ["display_media"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "content",
                    "status",
                    "publish_date",
                    "is_featured",
                ),
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "image",
                    "external_image_url",
                    "youtube_url",
                    "thumbnail",
                    "display_media",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Advertisement",
            {
                "fields": ("ad_type", "ad_code", "ad_image", "ad_url"),
                "classes": ("collapse",),
            },
        ),
        (
            "Resource",
            {
                "fields": ("resource_type", "resource_title", "resource"),
                "classes": ("collapse",),
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description", "meta_keywords"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(boolean=True, description="Ad")
    def has_ad(self, obj):
        return (
            (obj.ad_type != "none")
            or bool((obj.ad_code or "").strip())
            or bool(obj.ad_image)
            or bool(obj.ad_url)
        )

    def display_thumbnail(self, obj):
        image_url = obj.get_thumbnail_url()
        if image_url:
            return format_html('<img src="{}" width="50" />', image_url)
        return "-"

    display_thumbnail.short_description = "Thumbnail"

    def display_media(self, obj):
        html = []
        image_url = obj.get_image_url()
        youtube_url = obj.get_youtube_embed_url()

        if image_url:
            html.append(
                f'<div class="mb-4">'
                f"<strong>Image:</strong><br/>"
                f'<img src="{image_url}" width="200" />'
                f"</div>"
            )

        if youtube_url:
            html.append(
                f'<div class="mb-4">'
                f"<strong>YouTube Video:</strong><br/>"
                f'<iframe width="400" height="225" src="{youtube_url}" '
                f'frameborder="0" allowfullscreen></iframe>'
                f"</div>"
            )

        return format_html("".join(html)) if html else "-"

    display_media.short_description = "Media Preview"

    def clean_external_image_url(self, url):
        if not url:
            return url

        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("Invalid URL format")

        try:
            response = requests.head(url, allow_redirects=True)
            content_type = response.headers.get("content-type", "").lower()

            if not content_type.startswith("image/"):
                raise ValidationError("URL must point to an image file")

            if content_type not in [
                "image/jpeg",
                "image/jpg",
                "image/png",
                "image/webp",
            ]:
                raise ValidationError("Only JPG, PNG, and WEBP images are allowed")

        except requests.RequestException:
            raise ValidationError("Could not validate image URL")

        return url

    def save_model(self, request, obj, form, change):
        if "external_image_url" in form.changed_data:
            obj.external_image_url = self.clean_external_image_url(
                obj.external_image_url
            )
        super().save_model(request, obj, form, change)
