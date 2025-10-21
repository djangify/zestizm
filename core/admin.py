# core/admin.py
from django.contrib import admin
from .models import HomePageSettings, DashboardSettings, SupportRequest


@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for homepage, navbar, and footer content.
    Ensures only one record exists (singleton).
    """

    def has_add_permission(self, request):
        # Prevent creating multiple instances
        if HomePageSettings.objects.exists():
            return False
        return True

    fieldsets = (
        (
            "Navbar Settings",
            {
                "fields": (
                    "business_name",
                    "logo_image",
                ),
                "description": "Displayed in the site navbar. Logo appears next to the business name.",
            },
        ),
        (
            "Hero Section",
            {
                "fields": (
                    "hero_title",
                    "hero_paragraph",
                    "hero_image",
                ),
                "description": "Main hero content displayed on the homepage.",
            },
        ),
        (
            "Footer Information",
            {
                "fields": (
                    # Keep old paragraph temporarily for safe migration
                    # "business_paragraph",
                    ("social_1_name", "social_1_url"),
                    ("social_2_name", "social_2_url"),
                    "copyright_text",
                ),
                "description": "Footer text, optional old hero paragraph, and social media links.",
            },
        ),
        (
            "About Section (home-featured.html)",
            {
                "fields": (
                    "about_image",
                    "about_title",
                    "about_text",
                    ("about_cta_text", "about_cta_link"),
                ),
                "description": "Content for the left About box on the homepage.",
            },
        ),
        (
            "Download CTA Section (download-cta.html)",
            {
                "fields": (
                    "cta_title",
                    "cta_text",
                    ("cta_button_text", "cta_button_link"),
                    ("cta_secondary_text", "cta_secondary_link"),
                    "cta_image",
                    "cta_pdf_upload",
                ),
                "description": "Main call-to-action box for free downloads or lead magnets.",
            },
        ),
        (
            "Blog Section (blog-posts.html)",
            {
                "fields": (
                    "blog_section_title",
                    "blog_section_intro",
                ),
                "description": "Displayed above the blog posts grid.",
            },
        ),
        (
            "Optional / Global Settings",
            {
                "fields": (
                    "featured_products_title",
                    "additional_products_title",
                    "homepage_intro",
                    "announcement_bar_text",
                    "seo_meta_title",
                    "seo_meta_description",
                ),
                "description": "Optional homepage intro, announcement bar, and SEO metadata.",
            },
        ),
    )

    list_display = ("business_name", "updated")
    readonly_fields = ("updated",)

    class Media:
        css = {
            "all": ("admin/css/custom-admin.css",)  # Optional admin custom styling
        }


@admin.register(DashboardSettings)
class DashboardSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for Dashboard and Support section.
    """

    fieldsets = (
        (
            "Dashboard Header",
            {
                "fields": ("welcome_heading", "intro_text", "support_url"),
                "description": "Main dashboard greeting text and support link.",
            },
        ),
        (
            "Left Box — Get In Touch",
            {
                "fields": (
                    "left_title",
                    "response_time",
                    "support_hours",
                    ("policies_link", "docs_link"),
                ),
                "description": "Information shown in the left box of the Support page.",
            },
        ),
        (
            "Right Box — What I Can Help With",
            {
                "fields": (
                    "help_item_1",
                    "help_item_2",
                    "help_item_3",
                    "help_item_4",
                    "help_item_5",
                ),
                "description": "Five optional help topics displayed in the right support box.",
            },
        ),
    )

    list_display = ("__str__", "updated")

    class Meta:
        verbose_name = "Your Dashboard Settings"
        verbose_name_plural = "Your Dashboard Settings"

    def has_add_permission(self, request):
        # Enforce singleton pattern
        if DashboardSettings.objects.exists():
            return False
        return True


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "created_at", "handled")
    list_filter = ("handled", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
