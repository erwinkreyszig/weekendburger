from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from .models import Category, Product, Order, OrderContent, PaymentOption, AddOn


# Register your models here.

admin.site.register(PaymentOption)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order")
    list_editable = ("display_order",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("get_category", "name", "unit_price", "active")
    list_filter = ("category", "active")
    list_editable = ("name", "unit_price", "active")


class AddOnAdminInline(admin.TabularInline):
    model = AddOn
    extra = 1


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

    inlines = [AddOnAdminInline]


@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ("order_content", "product", "qty")
