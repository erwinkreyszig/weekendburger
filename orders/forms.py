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
        empty_label=None,
    )


class PremiumPattiesOrderContentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True, category__name="Premium Grilled Patties").order_by("name"),
        label="Premium Grilled Patties",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "categ": "Premium Grilled Patties"}),
        required=True,
    )


class ChickenBurgersOrderContentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True, category__name="Chicken Burgers").order_by("name"),
        label="Chicken Burgers",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "categ": "Chicken Burgers"}),
        required=True,
    )


class SmashBurgersOrderContentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True, category__name="Smash Burgers").order_by("name"),
        label="Smash Burgers",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "categ": "Smash Burgers"}),
        required=True,
    )


class DrinksOrderContentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True, category__name="Drinks").order_by("name"),
        label="Drinks",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "categ": "Drinks"}),
        required=True,
    )


class PancakesOrderContentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True, category__name="Pancakes").order_by("name"),
        label="Pancakes",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "categ": "Pancakes"}),
        required=True,
    )


class RiceMealsOrderContentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True, category__name="Rice Meals").order_by("name"),
        label="Rice Meals",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "categ": "Rice Meals"}),
        required=True,
    )


class SidesOrderContentFom(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True, category__name="Sides").order_by("name"),
        label="Sides",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "categ": "Sides"}),
        required=True,
    )


class AddOnsOrderContentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True, category__name="Add-ons").order_by("name"),
        label="Add-ons",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    qty = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "categ": "Add-Ons"}),
        required=True,
    )


class BaseOrderContentFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        counts = {}
        for form in self.forms:
            if not form.cleaned_data:
                continue
            product = form.cleaned_data.get("product", None)
            qty = form.cleaned_data.get("qty", None)
            if not product:  # also skip if only qty is entered
                continue
            qty = 0 if qty is None else qty
            counts[product] = counts.get(product, 0) + qty
        if any([qty < 1 for qty in list(counts.values())]):
            raise ValidationError(f"Entered {self.product} quantity is invalid.", code="not_positve_qty")


class PremiumPattiesOrderContentFormSet(BaseOrderContentFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOrderContentFormSet, self).__init__(*args, **kwargs)
        self.product = "Premium Grilled Patty"


class ChickenBurgersOrderContentFormSet(BaseOrderContentFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOrderContentFormSet, self).__init__(*args, **kwargs)
        self.product = "Chicken Burger"


class SmashBurgersOrderContentFormSet(BaseOrderContentFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOrderContentFormSet, self).__init__(*args, **kwargs)
        self.product = "Smash Burger"


class DrinksOrderContentFormSet(BaseOrderContentFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOrderContentFormSet, self).__init__(*args, **kwargs)
        self.product = "Drink"


class PancakesOrderContentFormSet(BaseOrderContentFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOrderContentFormSet, self).__init__(*args, **kwargs)
        self.product = "Pancake"


class RiceMealsOrderContentFormSet(BaseOrderContentFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOrderContentFormSet, self).__init__(*args, **kwargs)
        self.product = "Rice Meal"


class SidesOrderContentFormSet(BaseOrderContentFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOrderContentFormSet, self).__init__(*args, **kwargs)
        self.product = "Side"


class AddOnsOrderContentFormSet(BaseOrderContentFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOrderContentFormSet, self).__init__(*args, **kwargs)
        self.product = "Add-on"
