from django.urls import path
from . import views

urlpatterns = [
    path("", views.order_list, name="orders"),
    path("new/", views.create_order, name="new-order"),
    path("product_prices/", views.current_prices, name="product-prices"),
]
