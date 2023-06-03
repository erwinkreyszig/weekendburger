import pytz
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from .models import Category, Product, Order, OrderContent, PaymentOption, AddOn
from weekendburger.settings import TIME_ZONE


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
    readonly_fields = ("add_on_pk",)

    def add_on_pk(self, obj):
        return obj.pk


class OrderContentAdminInline(admin.TabularInline):
    model = OrderContent
    extra = 1
    readonly_fields = ("order_content_pk",)

    def order_content_pk(self, obj):
        return obj.pk


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
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
    inlines = [OrderContentAdminInline]


@admin.register(OrderContent)
class OrderContentAdmin(admin.ModelAdmin):
    list_display = ("pk", "order_pk", "order_info", "product", "qty")

    inlines = [AddOnAdminInline]

    @admin.display(empty_value="???")
    def order_pk(self, obj):
        return obj.order.pk

    @admin.display(empty_value="???")
    def order_info(self, obj):
        localized = obj.order.order_timestamp.astimezone(pytz.timezone(TIME_ZONE))
        return f"{localized.strftime('%b %d, %Y, %I:%M %p')} - {obj.order.taken_by.username}"


@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ("pk", "order_content_pk", "order_content", "product", "qty")

    @admin.display(empty_value="???")
    def order_content_pk(self, obj):
        return obj.order_content.pk
