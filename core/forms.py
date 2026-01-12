# core/forms.py

from django import forms
from core.models import Biobank, Collection, Tag


# ----------------------------------------------------------
# BIOBANK FORM
# ----------------------------------------------------------
class BiobankForm(forms.ModelForm):
    class Meta:
        model = Biobank
        fields = [
            "name",
            "institution",
            "visibility",
            "location_label",
            "latitude",
            "longitude",
            "notes",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "institution": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Search institution or address"
            }),
            "visibility": forms.Select(attrs={"class": "form-select"}),
            "location_label": forms.HiddenInput(),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Relevant notes about this Biobank"
            }),
        }


# ----------------------------------------------------------
# COLLECTION FORM
# ----------------------------------------------------------
class CollectionForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Collection
        fields = ["name", "biobank", "description", "tags"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Collection name"
            }),
            "biobank": forms.Select(attrs={
                "class": "form-select"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe the collection"
            }),
        }
# ----------------------------------------------------------
# TAG FORM
# ----------------------------------------------------------
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "description"]

