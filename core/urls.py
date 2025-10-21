from django.urls import path
from . import views
from django.views.generic import TemplateView


app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "create-mini-ecommerce",
        TemplateView.as_view(template_name="core/create-mini-ecommerce.html"),
        name="mini-ecommerce",
    ),
    path("support/", views.support, name="support"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
