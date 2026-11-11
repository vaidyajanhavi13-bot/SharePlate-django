from django.utils import timezone
from django import forms
from .models import Donation


class DonationForm(forms.ModelForm):
    pickup_deadline = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Donation
        fields = [
            "food_name",
            "description",
            "image",
            "quantity",
            "quantity_unit",
            "pickup_address",
            "pickup_deadline",
        ]

        widgets = {
            "food_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Vegetable rice"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "min": "1"}
            ),
            "quantity_unit": forms.Select(
                attrs={"class": "form-select"}
            ),
            "pickup_address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Pickup location"}
            ),
        }

    def clean_pickup_deadline(self):
        deadline = self.cleaned_data["pickup_deadline"]

        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(
                deadline,
                timezone.get_current_timezone()
            )

        return deadline