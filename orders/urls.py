from django.urls import path
from . import views

urlpatterns = [
    # path("old/", views.OrderListListView.as_view(), name="orders2"),
    path("", views.order_list, name="orders"),
    path("new/", views.create_order, name="new-order"),
    # path("old/", views.orders_list, name="orders-list"),
]
