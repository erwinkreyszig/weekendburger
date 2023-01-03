from orders.models import Category, Product, Order, OrderContent, PaymentOption, User


payment_opts_fields = ("code", "desc")
payment_opts_values = [("ca", "Cash"), ("fp", "Food Panda")]
for item in payment_opts_values:
    args = dict(zip(payment_opts_fields, item))
    PaymentOption.objects.create(**args)


category_fields = ("name", "desc")
category_values = [
    ("Smash Burgers", ""),
    ("Burgers", ""),
    ("Sides", ""),
    ("Add-ons", ""),
    ("Chicken", ""),
    ("Drinks", ""),
    ("Combo Meals", ""),
]
for item in category_values:
    Category.objects.create(**dict(zip(category_fields, item)))


cs = Category.objects.all()
cs_dict = {c.name: c for c in cs}

user = User.objects.get(email="vergil.ferrer.jp@gmail.com")

product_fields = ("name", "desc", "category", "unit_price", "active", "added_by")
product_values = [
    (
        "Classic Weekend Smash",
        "Smashed beef patty, caramelized onions, smash sauce and cheddar cheese slice",
        cs_dict.get("Smash Burgers"),
        105,
        True,
        user,
    ),
    (
        "Chili Weekend Smash",
        "Smashed beef patty, grilled green chili, smash sauce, caramelized onions, and ceddar cheese slice",
        cs_dict.get("Smash Burgers"),
        110,
        True,
        user,
    ),
    (
        "BBQ Weekend Smash",
        "Smashed beef patty, homemade BBQ sauce, smash sauce, caramelized onions, and cheddar cheese slice",
        cs_dict.get("Smash Burgers"),
        110,
        True,
        user,
    ),
    (
        "Breakfast Weekend Smash",
        "Smashed beef patty, bacon, egg, smash sauce, caramelized onions, and cheddar cheese slice",
        cs_dict.get("Smash Burgers"),
        135,
        True,
        user,
    ),
    ("Extra Cheese", "Bonus cheese", cs_dict.get("Add-ons"), 25, True, user),
    ("Extra Patty", "Bonus patty", cs_dict.get("Add-ons"), 40, True, user),
    (
        "Weekend Burger",
        "Grilled beef patty, homemade buttered buns, caramelized onions, lettuce, tomatoes, and 3 secret sauces",
        cs_dict.get("Burgers"),
        165,
        True,
        user,
    ),
    (
        "Cheese Burger",
        "Grilled beef patty, homemade buttered buns, bacon, caramelized onions, pickles, and secret cheese sauce",
        cs_dict.get("Burgers"),
        160,
        True,
        user,
    ),
    (
        "BBQ Burger",
        "Grilled beef patty, homemade buttered buns, onion rings, homemade bbq sauce",
        cs_dict.get("Burgers"),
        160,
        True,
        user,
    ),
    (
        "Juicy Weekend",
        "A premium burger with bacon jam, crispy bacon bits, secret sauce with american cheese slice on top and a surprise cheese inside the patty!",
        cs_dict.get("Burgers"),
        255,
        True,
        user,
    ),
    (
        "Homemade Parmesan Fries",
        "Fresh potatoes fried to perfection, topped with parsley and parmesan cheese",
        cs_dict.get("Sides"),
        60,
        True,
        user,
    ),
    (
        "Onion Rings",
        "Beer-battered white onions fried to perfection! Comes with a special mayo dip.",
        cs_dict.get("Sides"),
        65,
        True,
        user,
    ),
    (
        "Soy Honey Chicken Wings",
        "Crispy and tasty chicken wings with homemade soy honey sauce. Servings: 6pcs.",
        cs_dict.get("Chicken"),
        220,
        True,
        user,
    ),
    (
        "Buffalo Chicken Wings",
        "Crispy and tasty chicken wings with homemade original buffalo sauce. Servings: 6pcs.",
        cs_dict.get("Chicken"),
        220,
        True,
        user,
    ),
    (
        "Milkshake",
        "Refreshing original homemade milkshake with chocolate fudge and chocolate ice cream",
        cs_dict.get("Drinks"),
        105,
        True,
        user,
    ),
]
for item in product_values:
    Product.objects.create(**dict(zip(product_fields, item)))
