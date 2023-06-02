from django.urls import path
from . import views

urlpatterns = [
    path("", views.order_list, name="orders"),
    path("new/", views.create_order, name="new-order"),
    path("products/", views.get_products, name="products-all"),
    path("product_prices/", views.current_prices, name="product-prices"),
    path("print_order/", views.print_order, name="print-order"),
    path("print_order/<int:id>/", views.print_order, name="print-order"),
    path("aggregate_orders/", views.aggregate_orders, name="aggregate-orders"),
    path("aggregate_orders/<fromdate>/", views.aggregate_orders, name="aggregate-orders"),
    path("aggregate_orders/<fromdate>/<todate>/", views.aggregate_orders, name="aggregate-orders"),
]
