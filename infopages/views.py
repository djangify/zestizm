from django.views.generic import ListView, DetailView
from bs4 import BeautifulSoup
from .models import InfoPage


class PolicyListView(ListView):
    model = InfoPage
    template_name = "infopages/policy_index.html"
    context_object_name = "pages"

    def get_queryset(self):
        return InfoPage.objects.filter(page_type="policy", published=True)


class DocListView(ListView):
    model = InfoPage
    template_name = "infopages/docs_index.html"
    context_object_name = "pages"

    def get_queryset(self):
        return InfoPage.objects.filter(page_type="doc", published=True)


class InfoPageDetailView(DetailView):
    model = InfoPage
    template_name = "infopages/detail.html"
    context_object_name = "page"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Parse content and build a table of contents
        soup = BeautifulSoup(self.object.content or "", "html.parser")
        toc = []
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True)
            if not text:
                continue
            if "id" not in heading.attrs:
                heading["id"] = text.lower().replace(" ", "-").replace(".", "")
            toc.append({"title": text, "id": heading["id"]})

        # Save updated HTML + TOC to context
        context["toc"] = toc
        context["rendered_content"] = str(soup)
        return context
