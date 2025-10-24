from django.urls import path
from . import views


app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("support/", views.support, name="support"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
