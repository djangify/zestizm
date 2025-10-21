from django.urls import path
from . import views

app_name = "infopages"

urlpatterns = [
    path("policies/", views.PolicyListView.as_view(), name="policy_index"),
    path("docs/", views.DocListView.as_view(), name="docs_index"),
    path(
        "policies/<slug:slug>/",
        views.InfoPageDetailView.as_view(),
        name="policy_detail",
    ),
    path("docs/<slug:slug>/", views.InfoPageDetailView.as_view(), name="doc_detail"),
]
