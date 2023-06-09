import pytz, json, re
from weekendburger.settings import TIME_ZONE
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, When, Case, Value, Q, Prefetch
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from .forms import (
    OrderRangeForm,
    OrderForm,
)
from .models import Order, OrderContent, Product, Category, PaymentOption, AddOn
from .permissions import user_can_do, CAN_ADD_ORDER_PERM, CAN_VIEW_ORDER_PERM, CAN_VIEW_REPORT_PERM

# Create your views here.

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%b %d, %Y %I:%M %p"
NUM_ITEMS_DEFAULT = 10
PAGE_NUM_DEFAULT = 1


@login_required
@user_can_do(permissions=(CAN_VIEW_ORDER_PERM, CAN_ADD_ORDER_PERM))
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

    status_whens = [When(order_status=k, then=Value(v)) for k, v in Order.ORDER_STATUSES]
    type_whens = [When(order_type=k, then=Value(v)) for k, v in Order.ORDER_TYPES]

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
    category_qs = Category.objects.only("name")
    product_qs = Product.objects.prefetch_related(Prefetch("category", queryset=category_qs)).only(
        "name", "category__name"
    )
    order_contents_raw = OrderContent.objects.filter(order_id__in=order_data)
    order_contents = (
        order_contents_raw.prefetch_related(Prefetch("product", queryset=product_qs))
        .annotate(
            name=F("product__name"),
            category=F("product__category__name"),
            price=F("price_at_order"),
            add_on_allowed=F("product__add_on_allowed"),
        )
        .values("pk", "order_id", "name", "category", "price", "qty", "add_on_allowed")
    )

    add_ons = (
        AddOn.objects.prefetch_related(Prefetch("product", queryset=Product.objects.only("name")))
        .filter(order_content_id__in=order_contents_raw.values("pk"))
        .annotate(name=F("product__name"), price=F("price_at_order"))
        .values("order_content_id", "name", "qty", "price")
    )
    add_ons_dict = {}
    for add_on in add_ons:
        add_ons_dict.setdefault(add_on.pop("order_content_id"), []).append(add_on)
    # add add_ons to order_content
    for oc in order_contents:
        oc["add-ons"] = add_ons_dict.get(oc["pk"], None)

    for oc in order_contents:
        order_data[oc.pop("order_id")].setdefault("contents", []).append(oc)

    # calculate totals
    for inner_dict in order_data.values():
        _total = 0
        contents = inner_dict.get("contents")
        for item in contents:
            price = item.get("price")
            qty = item.get("qty")
            _total += price * qty
            add_ons = item.get("add-ons") if item.get("add-ons") else []
            for add_on in add_ons:
                a_price = add_on.get("price")
                a_qty = add_on.get("qty")
                a_total = (a_price * a_qty) * qty
                _total += a_total
        inner_dict["total"] = _total
        total += _total

    # page count
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
        "permissions": list(request.user.get_all_permissions()),
        "username": request.user.username,
    }

    if request.method == "GET":
        return render(request, "orders_list.html", context=context)
    context.pop("page")
    context.pop("form")
    return JsonResponse(context)


@login_required
@user_can_do(permissions=(CAN_ADD_ORDER_PERM,))
def get_products(request):
    if request.method != "GET":
        return JsonResponse({})
    products = (
        Product.objects.filter(active=True)
        .select_related("category")
        .values("pk", "name", "desc", "category__name", "category__pk", "unit_price", "add_on_allowed")
        .order_by("category__display_order")
    )
    categorized_products = {}
    categories = []
    category_data = {}
    for product in products:
        category_pk = product["category__pk"]
        category_name = product["category__name"]
        product.pop("category__pk")
        product.pop("category__name")
        categorized_products.setdefault(category_name, []).append(product)
        category_data[category_pk] = category_name
        # this is to preserve order
        if category_name not in categories and category_name != "Add-ons":
            categories.append(category_name)
    return JsonResponse(
        {"product_data": categorized_products, "categories": categories, "category_data": category_data}
    )


@login_required
@user_can_do(permissions=(CAN_ADD_ORDER_PERM,))
def create_order(request):
    now = timezone.now()
    order_data = {}

    if request.method == "POST":
        ORDER_STATUS_FIXED_TMP = "pa"  # hardcode this for now
        data = json.loads(request.POST.get("data"))  # same format as currentOrders from frontend
        order_date = request.POST.get("order_date")
        order_type = request.POST.get("order_type")
        payment_type = request.POST.get("payment_type")
        total = request.POST.get("total")

        year, month, day = map(int, order_date.split("-", 2))
        order_types_dict = {otype[1]: otype[0] for otype in Order.ORDER_TYPES}
        payment_type_code = re.findall(r"\([a-z]+\)", payment_type)[0][1:-1]
        payment_type_obj = PaymentOption.objects.get(code=payment_type_code)
        unit_prices_dict = dict(Product.objects.values_list("name", "unit_price"))
        products_dict = {p.name: p for p in Product.objects.all()}

        all_items_saved = True
        with transaction.atomic():
            # create order
            order = Order.objects.create(
                order_timestamp=now.replace(year=year, month=month, day=day),
                order_type=order_types_dict.get(order_type),
                taken_by=request.user,
                order_status=ORDER_STATUS_FIXED_TMP,
                paid_by=payment_type_obj,
            )
            if not order:
                raise Exception("An error occurred in saving order data")
            # save order contents
            calculated_total = 0
            for product_name, content in data.items():
                product_name = product_name.split("|", 1)[0]
                product = products_dict.get(product_name)
                qty = int(content.get("qty"))
                current_price = unit_prices_dict.get(product_name)
                calculated_total += qty * current_price
                # save product
                order_content = OrderContent.objects.create(
                    order=order, product=product, qty=qty, price_at_order=current_price
                )
                if not order_content:
                    all_items_saved = False
                    continue  # skip saving add-ons attached to order content if not properly created
                if add_ons := content.get("add-ons", None):
                    for add_on_name, add_on_qty in add_ons.items():
                        add_on = products_dict.get(add_on_name)
                        current_price = unit_prices_dict.get(add_on_name)
                        calculated_total += int(add_on_qty) * current_price * qty
                        saved = AddOn.objects.create(
                            order_content=order_content,
                            product=add_on,
                            qty=int(add_on_qty),
                            price_at_order=current_price,
                        )
                        if not saved:
                            all_items_saved = False
                            break  # break out of add-on creation
            if not all_items_saved:
                raise Exception("reverting transaction")
        print(f"calculated_total: {calculated_total}, total: {total}, all_items_saved: {all_items_saved}")
        if all_items_saved and int(total) == calculated_total:
            return JsonResponse({"saved": True, "ref": order.pk})
        return JsonResponse({"saved": False})
    else:
        order_form = OrderForm()

    context = {
        "order_form": order_form,
        "order_data": order_data,
        "page": "new-order",
        "permissions": list(request.user.get_all_permissions()),
        "username": request.user.username,
    }

    return render(request, "new_order_v2.html", context)


@login_required
@user_can_do(permissions=(CAN_ADD_ORDER_PERM,))
def current_prices(request):
    if request.method == "GET":
        prices_dict = dict(Product.objects.filter(active=True).values_list("name", "unit_price"))
        return JsonResponse(prices_dict)
    return JsonResponse({})


@login_required
@user_can_do(permissions=(CAN_ADD_ORDER_PERM, CAN_VIEW_ORDER_PERM))
def print_order(request, id=None):
    context = {"show": False}
    if id:
        if order := Order.objects.filter(pk=id).first():
            context["show"] = True
            context["id"] = id
            context["date"] = order.order_timestamp.astimezone(pytz.timezone(TIME_ZONE)).strftime(DATETIME_FORMAT)
            order_types = dict(Order.ORDER_TYPES)
            context["type"] = order_types.get(order.order_type)
            context["payment_opt"] = order.paid_by.desc
            contents = []
            total = 0
            for oc in order.ordercontent_set.prefetch_related("addon_set"):
                sub_total = oc.qty * oc.price_at_order
                total += sub_total
                add_ons = list(
                    oc.addon_set.annotate(
                        product_name=F("product__name"),
                        price=F("price_at_order"),
                        subtotal=F("qty") * F("price_at_order") * F("order_content__qty"),
                    ).values("product_name", "qty", "price", "subtotal")
                )
                oc_dict = {
                    "product_name": oc.product.name,
                    "qty": oc.qty,
                    "price": oc.price_at_order,
                    "subtotal": sub_total,
                    "addons": add_ons,
                }
                total += sum(add_on["subtotal"] for add_on in add_ons)
                contents.append(oc_dict)
            context["contents"] = contents
            context["total"] = total

    return render(request, "print_order.html", context)


@login_required
@user_can_do(permissions=(CAN_VIEW_REPORT_PERM,))
def aggregate_orders(request, fromdate=None, todate=None):
    context = {"show": False, "msg": ""}
    try:
        fromdate = datetime.strptime(fromdate, DATE_FORMAT) if fromdate else None
        todate = datetime.strptime(todate, DATE_FORMAT) if todate else None
    except ValueError:
        context["msg"] = "Parameters have the incorrect date format (YYYY-MM-DD)."
        return render(request, "aggregate_orders.html", context)
    if (fromdate and todate) and fromdate > todate:
        context["msg"] = "Invalid date parameters."
        return render(request, "aggregate_orders.html", context)
    if not fromdate:
        context["msg"] = "Needs a date for the start of period."
        return render(request, "aggregate_orders.html", context)
    if not todate:
        todate = fromdate

    fromdate = fromdate.replace(hour=0, minute=0, second=0)
    todate = todate.replace(hour=23, minute=59, second=59)

    order_pks = Order.objects.filter(
        Q(order_timestamp__gte=timezone.make_aware(fromdate)) & Q(order_timestamp__lte=timezone.make_aware(todate))
    ).values_list("pk", flat=True)
    category_qs = Category.objects.only("name")
    product_qs = Product.objects.prefetch_related(Prefetch("category", queryset=category_qs)).only(
        "category__name", "name"
    )
    contents = (
        OrderContent.objects.prefetch_related(Prefetch("product", queryset=product_qs))
        .filter(order__pk__in=order_pks)
        .order_by("product__category__name", "product__name")
    )
    aggregated = {}
    grand_total = 0
    for item in contents:
        key = (item.product_id, item.price_at_order)
        subtotal = item.qty * item.price_at_order
        grand_total += subtotal
        if key not in aggregated:
            aggregated[key] = {
                "category": item.product.category.name,
                "product": item.product.name,
                "qty": item.qty,
                "price": item.price_at_order,
                "total": subtotal,
            }
        else:
            aggregated[key]["qty"] += item.qty
            aggregated[key]["total"] += subtotal
    aggregated_addons = {}
    oc_pks = contents.values("pk")
    add_ons = AddOn.objects.select_related("order_content").filter(order_content__pk__in=oc_pks)
    for add_on in add_ons:
        key = (add_on.product_id, add_on.price_at_order)
        subtotal = add_on.qty * add_on.price_at_order * add_on.order_content.qty
        grand_total += subtotal
        if key not in aggregated_addons:
            aggregated_addons[key] = {
                "category": "Add-ons",
                "product": add_on.product.name,
                "qty": add_on.qty * add_on.order_content.qty,
                "price": add_on.price_at_order,
                "total": subtotal,
            }
        else:
            aggregated_addons[key]["qty"] += add_on.qty * add_on.order_content.qty
            aggregated_addons[key]["total"] += subtotal
    context["show"] = True
    context["fromdate"] = f'{fromdate.strftime("%b %d, %Y")} 00:00:00'
    context["todate"] = f'{todate.strftime("%b %d, %Y")} 23:59:59'
    context["data"] = aggregated
    context["data_addons"] = aggregated_addons
    context["grand_total"] = grand_total

    return render(request, "aggregate_orders.html", context)
