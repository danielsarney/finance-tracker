from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "icon", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., fa-utensils, fa-car",
                }
            ),
            "color": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
        }
