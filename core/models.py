# core/models.py
from django.db import models
from tinymce.models import HTMLField


class SupportRequest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} from {self.name}"


class HomePageSettings(models.Model):
    """
    A single editable record controlling homepage, navbar, and footer content.
    """

    # --- Business / Navbar Info ---
    business_name = models.CharField(
        "Business Name",
        max_length=150,
        default="Djangify",
        help_text="Displayed in the navbar next to the logo.",
    )
    business_paragraph = models.TextField(
        "Deprecated – previously Hero Paragraph",
        blank=True,
        null=True,
        help_text="Old hero paragraph, now replaced by hero_paragraph. Safe to delete once migrated.",
    )
    logo_image = models.ImageField(
        "Logo Image",
        upload_to="homepage/logo/",
        blank=True,
        null=True,
        help_text="Optional logo to display in the navbar beside the business name.",
    )

    # --- Hero Section ---
    hero_title = models.CharField(
        "Hero Title",
        max_length=150,
        default="Your Main Title",
        help_text="Main heading text displayed in the hero section.",
    )
    hero_paragraph = models.TextField(
        "Hero Paragraph",
        help_text="Supporting 1–2 sentences displayed below the hero title.",
        blank=True,
        null=True,
    )
    hero_image = models.ImageField(
        upload_to="homepage/hero/",
        blank=True,
        null=True,
        help_text="Optional hero background image (recommended 700×500px).",
    )

    # --- Footer Info ---
    social_1_name = models.CharField(
        max_length=50, blank=True, null=True, help_text="e.g. LinkedIn"
    )
    social_1_url = models.URLField(blank=True, null=True)
    social_2_name = models.CharField(
        max_length=50, blank=True, null=True, help_text="e.g. Instagram"
    )
    social_2_url = models.URLField(blank=True, null=True)
    copyright_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional custom copyright text. Leave blank to auto-generate.",
    )

    # --- About Box (home-featured.html) ---
    about_image = models.ImageField(
        upload_to="homepage/",
        blank=True,
        null=True,
        help_text="Upload a small logo image (max display size 128×128px)",
    )
    about_title = models.CharField(max_length=150, default="Your Title Here")
    about_text = HTMLField(
        help_text="Text for the About box section – around 70–100 words recommended."
    )
    about_cta_text = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Optional small CTA below paragraph.",
    )
    about_cta_link = models.URLField(blank=True, null=True)

    # --- Download CTA Section ---
    cta_title = models.CharField(
        max_length=200, default="Free Download: Title For Your Download"
    )
    cta_text = HTMLField(blank=True, null=True, help_text="Intro text for the CTA box.")
    cta_button_text = models.CharField(max_length=100, default="Here Is Your Download")
    cta_button_link = models.URLField(blank=True, null=True)
    cta_secondary_text = models.CharField(
        max_length=100, default="Explore Our Shop", blank=True
    )
    cta_secondary_link = models.URLField(blank=True, null=True)
    cta_image = models.ImageField(upload_to="homepage/", blank=True, null=True)
    cta_pdf_upload = models.FileField(upload_to="homepage/pdfs/", blank=True, null=True)

    # --- Blog Posts Section ---
    blog_section_title = models.CharField(
        max_length=150,
        default="Latest Blog Posts",
        help_text="Displayed above the blog posts grid.",
    )
    blog_section_intro = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Short paragraph introducing the blog section (500 words or less).",
    )

    # --- Optional / Meta ---
    featured_products_title = models.CharField(
        max_length=150, default="Featured Products"
    )
    additional_products_title = models.CharField(
        max_length=150, default="More to Explore"
    )
    homepage_intro = models.TextField(blank=True, null=True)
    announcement_bar_text = models.CharField(max_length=200, blank=True, null=True)
    seo_meta_title = models.CharField(max_length=150, blank=True, null=True)
    seo_meta_description = models.CharField(max_length=255, blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Home Page Settings"
        verbose_name_plural = "Home Page Settings"

    def __str__(self):
        return "Home Page Content"

    def save(self, *args, **kwargs):
        if not self.pk and HomePageSettings.objects.exists():
            raise ValueError("Only one HomePageSettings instance is allowed.")
        super().save(*args, **kwargs)

    @property
    def get_copyright(self):
        return self.copyright_text or f"© {self.business_name}. All rights reserved."


class DashboardSettings(models.Model):
    """
    Controls the text, support details, and help items shown
    on the customer dashboard and support page.
    Singleton pattern – only one instance allowed.
    """

    # --- Dashboard Header ---
    welcome_heading = models.CharField(
        max_length=150,
        default="Welcome,",
        help_text="Main heading text at the top of the dashboard.",
    )
    intro_text = models.TextField(
        blank=True,
        null=True,
        default="Here’s an overview of your account and quick access to your saved items.",
        help_text="Displayed under the welcome heading on the dashboard.",
    )
    support_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional custom URL for the support/contact page. Defaults to /support/.",
    )

    # --- Left Box: Get In Touch ---
    left_title = models.CharField(
        max_length=100,
        default="Get In Touch",
        help_text="Title for the left box on the support page.",
    )
    response_time = models.CharField(
        max_length=100,
        default="Within 48 hours (weekdays)",
        help_text="Displayed response time.",
    )
    support_hours = models.CharField(
        max_length=100,
        default="Monday – Friday, 9AM – 4PM GMT",
        help_text="Displayed support hours.",
    )
    policies_link = models.URLField(
        blank=True, null=True, help_text="Optional link to policies index page."
    )
    docs_link = models.URLField(
        blank=True, null=True, help_text="Optional link to documentation page."
    )

    # --- Right Box: What I Can Help With ---
    help_item_1 = models.CharField(max_length=120, blank=True, null=True)
    help_item_2 = models.CharField(max_length=120, blank=True, null=True)
    help_item_3 = models.CharField(max_length=120, blank=True, null=True)
    help_item_4 = models.CharField(max_length=120, blank=True, null=True)
    help_item_5 = models.CharField(max_length=120, blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard Settings"
        verbose_name_plural = "Dashboard Settings"

    def __str__(self):
        return "Dashboard Settings"

    def save(self, *args, **kwargs):
        if not self.pk and DashboardSettings.objects.exists():
            raise ValueError("Only one DashboardSettings instance is allowed.")
        super().save(*args, **kwargs)
