from django import forms
from django.core.exceptions import ValidationError
from django.forms.formsets import BaseFormSet
from django.utils import timezone
from .models import Order, PaymentOption, Product


class OrderRangeForm(forms.Form):
    start_date = forms.DateField(
        label="Start Date",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "placeholder": "Start Date",
                "aria-label": "Start Date",
                "readonly": "readonly",
            }
        ),
        required=True,
        initial=timezone.now().strftime("%Y-%m-%d"),
    )
    end_date = forms.DateField(
        label="End Date",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "placeholder": "End Date",
                "aria-label": "End Date",
                "readonly": "readonly",
            }
        ),
        required=False,
    )
    items = forms.IntegerField(
        label="Rows",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Items",
                "aria-label": "Rows per page",
            }
        ),
        initial=10,
    )


class OrderContentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True).order_by("category__name"),
        label="Product",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quatity",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=True,
    )


class OrderForm(forms.Form):
    order_date = forms.DateField(
        label="Order Date",
        widget=forms.DateInput(
            attrs={"class": "form-control", "readonly": "readonly"},
        ),
        required=True,
        initial=timezone.now().strftime("%Y-%m-%d"),
    )
    order_type = forms.CharField(
        label="Type",
        widget=forms.Select(
            attrs={"class": "form-control"},
            choices=Order.ORDER_TYPES,
        ),
        required=True,
    )
    payment_option = forms.ModelChoiceField(
        queryset=PaymentOption.objects.all(),
        label="Payment option",
        widget=forms.Select(
            attrs={"class": "form-control"},
        ),
        required=True,
    )


class BaseOrderContentFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        counts = {}
        for form in self.forms:
            product = form.cleaned_data.get("product")
            qty = form.cleaned_data.get("qty")
            counts[product] = counts.get(product, 0) + qty
        if any([qty < 1 for qty in list(counts.values())]):
            raise ValidationError("Cannot have a negative quantity.", code="not_positve_qty")
