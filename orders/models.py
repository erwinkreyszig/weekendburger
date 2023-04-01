from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from simple_history import register

# Create your models here.

register(User)

DT_FORMAT = "%Y-%m-%d %H:%M:%S"


class Category(models.Model):
    """Model representing the category of a product"""

    name = models.CharField(max_length=40, unique=True)
    desc = models.CharField(max_length=100, null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Model representing a product"""

    name = models.CharField(max_length=255, help_text="Enter a product name")
    desc = models.TextField(null=True, blank=True, help_text="Product description goes here")
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, null=True, blank=True)
    unit_price = models.IntegerField()
    add_on_allowed = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    added_timestamp = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["category", "name", "active"]

    def __str__(self):
        return self.name

    def get_category(self):
        return self.category.name if self.category else ""

    def get_absolute_url(self):
        return reverse("product", args=[str(self.id)])


class Order(models.Model):
    """Model representing an order"""

    ORDER_TYPES = (
        ("st", "In-store"),
        ("dl", "Delivery"),
        ("pu", "Pick-up"),
        ("fp", "Food Panda"),
    )
    ORDER_STATUSES = (
        ("ip", "In-progress"),
        ("pa", "Paid"),
        ("pe", "Pending"),
        ("ca", "Cancelled"),
    )

    order_timestamp = models.DateTimeField(default=timezone.now)
    order_type = models.CharField(max_length=2, choices=ORDER_TYPES)
    taken_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO: change default to False when mechanism for confrming order is added
    is_paid = models.BooleanField(default=True)
    order_status = models.CharField(max_length=2, choices=ORDER_STATUSES, default="ip")
    paid_by = models.ForeignKey("PaymentOption", on_delete=models.SET_NULL, null=True, blank=False)

    history = HistoricalRecords()

    class Meta:
        ordering = ["order_timestamp", "is_paid", "order_type"]

    def __str__(self):
        return f"{self.order_timestamp.strftime(DT_FORMAT)} - {self.taken_by}"

    def get_absolute_url(self):
        return reverse("order", args=[str(self.id)])


class OrderContent(models.Model):
    """Model representing the contents of an order"""

    order = models.ForeignKey(Order, on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    qty = models.PositiveIntegerField(default=1)
    price_at_order = models.IntegerField(default=0)

    history = HistoricalRecords()

    def __str__(self):
        return self.order.order_timestamp.strftime(DT_FORMAT)


class AddOn(models.Model):
    """
    Model representing an order add-on
    This should only be attached to order contents with product.add_on_allowed = True
    """

    order_content = models.ForeignKey(OrderContent, on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    qty = models.PositiveBigIntegerField(default=1)
    price_at_order = models.IntegerField(default=0)

    history = HistoricalRecords()

    def __str__(self):
        return self.order_content.order.order_timestamp.strftime(DT_FORMAT)


class PaymentOption(models.Model):
    """Model representing a payment option"""

    code = models.CharField(max_length=4, unique=True)
    desc = models.CharField(max_length=100, null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.desc} ({self.code})"
