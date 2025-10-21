from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField


class InfoPage(models.Model):
    PAGE_TYPE_CHOICES = [
        ("policy", "Policy"),
        ("doc", "Documentation"),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(
        unique=True, help_text="Used in the page URL, e.g. /policies/terms/"
    )
    page_type = models.CharField(max_length=10, choices=PAGE_TYPE_CHOICES)
    content = HTMLField(
        help_text="Main page content. You can use headings, lists, and links."
    )
    last_updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["page_type", "title"]
        verbose_name = "Info Page"
        verbose_name_plural = "Info Pages"

    def __str__(self):
        return f"{self.title} ({self.page_type})"

    def get_absolute_url(self):
        if self.page_type == "policy":
            return reverse("infopages:policy_detail", kwargs={"slug": self.slug})
        return reverse("infopages:doc_detail", kwargs={"slug": self.slug})
