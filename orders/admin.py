from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from .models import Category, Product, Order, OrderContent, PaymentOption


# Register your models here.

admin.site.register(Category)
admin.site.register(PaymentOption)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("get_category", "name", "unit_price", "active")
    list_filter = ("category", "active")


class OrderAdminInline(admin.TabularInline):
    model = OrderContent
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_timestamp",
        "order_type",
        "taken_by",
        "order_status",
        "is_paid",
        "paid_by",
    )
    list_filter = (
        ("order_timestamp", DateFieldListFilter),
        "order_type",
        "taken_by",
        "order_status",
        "paid_by",
    )
    inlines = [OrderAdminInline]


@admin.register(OrderContent)
class OrderContentAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "qty")
