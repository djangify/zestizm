# shop/forms.py
from django import forms
from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(attrs={"class": "hidden peer"}),
            "comment": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-700",
                    "rows": 4,
                    "placeholder": "Only verified buyers can review. Thank you, for sharing your thoughts about this product...",
                }
            ),
        }
