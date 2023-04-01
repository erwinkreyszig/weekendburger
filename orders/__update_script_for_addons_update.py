from orders.models import Product


products = Product.objects.filter(category__name__in=("Chicken Burgers", "Premium Grilled Patties", "Smash Burgers"))
for product in products:
    product.add_on_allowed = True
    product.save()
