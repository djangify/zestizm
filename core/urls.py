from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("support/", views.support, name="support"),
    path(
        "zest-for-life/",
        TemplateView.as_view(template_name="core/zest-for-life.html"),
        name="zest-for-life/",
    ),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
