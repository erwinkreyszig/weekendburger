import pytz
from weekendburger.settings import TIME_ZONE
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, When, Case, Value
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from .forms import OrderForm, OrderContentForm, BaseOrderContentFormSet, OrderRangeForm
from .models import Order, OrderContent

# Create your views here.

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%b %d, %Y %I:%M %p"
NUM_ITEMS_DEFAULT = 10
PAGE_NUM_DEFAULT = 1


@login_required
def order_list(request):
    start_date = datetime.now()
    end_date = None
    num_items = NUM_ITEMS_DEFAULT
    page_num = PAGE_NUM_DEFAULT
    total = 0

    if request.method == "POST":
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        num_items = request.POST["items"]
        page_num = request.POST["page_num"]
        start_date = datetime.strptime(start_date, DATE_FORMAT) if start_date else datetime.now()
        end_date = datetime.strptime(end_date, DATE_FORMAT) if end_date else None
        num_items = int(num_items) if num_items else NUM_ITEMS_DEFAULT
        page_num = int(page_num) if page_num else PAGE_NUM_DEFAULT

    status_whens = []
    for k, v in Order.ORDER_STATUSES:
        status_whens.append(When(order_status=k, then=Value(v)))
    type_whens = []
    for k, v in Order.ORDER_TYPES:
        type_whens.append(When(order_type=k, then=Value(v)))
    orders = (
        Order.objects.select_related("taken_by", "paid_by")
        .order_by("-order_timestamp")
        .annotate(
            payment_method=F("paid_by__desc"),
            user=F("taken_by__username"),
            status=Case(*status_whens, default=Value(Order.ORDER_STATUSES[0][1])),
            type=Case(*type_whens, default=Value(Order.ORDER_TYPES[0][1])),
        )
        .values(
            "pk",
            "order_timestamp",
            "type",
            "user",
            "status",
            "is_paid",
            "payment_method",
        )
        .filter(
            order_timestamp__gte=timezone.make_aware(start_date.replace(hour=0, minute=0, second=0, microsecond=0)),
        )
    )
    if not end_date:
        end_date = start_date
    orders = orders.filter(order_timestamp__lt=timezone.make_aware(end_date.replace(hour=23, minute=59, second=59)))
    # change order_timestamp to string type
    for order in orders:
        order["order_timestamp"] = (
            order["order_timestamp"].astimezone(pytz.timezone(TIME_ZONE)).strftime(DATETIME_FORMAT)
        )

    paginator = Paginator(orders, num_items)
    page_obj = paginator.get_page(page_num)
    # change this to a dict with order pk as keys to be able to be populated with order contents
    order_data = {order.get("pk"): order for order in list(page_obj.object_list)}
    order_contents = (
        OrderContent.objects.filter(order_id__in=order_data)
        .select_related("product", "product_category")
        .annotate(
            name=F("product__name"),
            category=F("product__category__name"),
            price=F("price_at_order"),
        )
        .values("order_id", "name", "category", "price", "qty")
    )
    for oc in order_contents:
        order_data[oc.pop("order_id")].setdefault("contents", []).append(oc)

    # calculate totals
    for inner_dict in order_data.values():
        _total = 0
        for f, v in inner_dict.items():
            if f == "contents":
                _total = sum([r.get("qty") * r.get("price") for r in v])
        inner_dict["total"] = _total
        total += _total

    total_items = orders.count()
    quot, rem = divmod(total_items, num_items)
    total_pages = quot + 1 if rem != 0 else quot

    context = {
        "start_date": start_date.strftime(DATE_FORMAT),
        "end_date": end_date.strftime(DATE_FORMAT) if end_date else end_date,
        "orders": list(order_data.values()),
        "total_items": total_items,
        "num_items": num_items,
        "total_pages": total_pages,
        "page_num": page_num,
        "page": "orders-list",
        "form": OrderRangeForm(
            initial={
                "start_date": start_date.strftime(DATE_FORMAT),
                "items": num_items,
            }
        ),
        "total": total,
    }

    if request.method == "GET":
        return render(request, "orders_list.html", context=context)
    context.pop("page")
    context.pop("form")
    return JsonResponse(context)


@login_required
def create_order(request):
    OrderContentFormset = formset_factory(OrderContentForm, formset=BaseOrderContentFormSet, extra=1)

    if request.method == "POST":
        ORDER_STATUS_FIXED_TMP = "pa"  # hardcode this for now
        now = timezone.now()
        order_form = OrderForm(request.POST)
        order_content_formset = OrderContentFormset(request.POST)

        if order_form.is_valid() and order_content_formset.is_valid():
            order_date = order_form.cleaned_data.get("order_date")
            order_type = order_form.cleaned_data.get("order_type")
            payment_option = order_form.cleaned_data.get("payment_option")

            with transaction.atomic():
                # create order
                order = Order.objects.create(
                    order_timestamp=now.replace(year=order_date.year, month=order_date.month, day=order_date.day),
                    order_type=order_type,
                    taken_by=request.user,
                    order_status=ORDER_STATUS_FIXED_TMP,
                    paid_by=payment_option,
                )
                if not order:
                    raise Exception("An error occurred in saving Order data")

                # as the order content in the front end does not care if there are duplicate items,
                # this part will consolidate the same products, i.e. if two of the same product
                # was ordered, those two rows will show up as one with the quantities totaled
                order_contents_cleaned = {}
                for ocf in order_content_formset:
                    product = ocf.cleaned_data.get("product")
                    qty = ocf.cleaned_data.get("qty")
                    order_contents_cleaned[product] = order_contents_cleaned.get(product, 0) + qty
                for product, qty in order_contents_cleaned.items():
                    OrderContent.objects.create(
                        order=order, product=product, qty=qty, price_at_order=product.unit_price
                    )
            return HttpResponseRedirect("/orders/")
    else:
        order_form = OrderForm()
        order_content_formset = OrderContentFormset()

    context = {
        "order_form": order_form,
        "order_content_formset": order_content_formset,
        "page": "new-order",
    }

    return render(request, "new_order.html", context)
