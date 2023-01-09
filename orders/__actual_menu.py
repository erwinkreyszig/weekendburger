from orders.models import Category, Product, PaymentOption, User


# create payment options
payment_opts_fields = ("code", "desc")
payment_opts_values = [("ca", "Cash"), ("fp", "Food Panda")]
for item in payment_opts_values:
    args = dict(zip(payment_opts_fields, item))
    PaymentOption.objects.create(**args)

# create categories
category_fields = ("name", "desc")
category_values = [
    ("Premium Grilled Patties", ""),
    ("Chicken Burgers", ""),
    ("Smash Burgers", ""),
    ("Drinks", ""),
    ("Pancakes", ""),
    ("Rice Meals", ""),
    ("Sides", ""),
    ("Add-ons", ""),
]
for item in category_values:
    Category.objects.create(**dict(zip(category_fields, item)))

# create products
cs = Category.objects.all()
cs_dict = {c.name: c for c in cs}

user = User.objects.get(email="vergil.ferrer.jp@gmail.com")

product_fields = ("name", "desc", "category", "unit_price", "active", "added_by")
product_values = [
    (
        "Weekend Burger",
        "100% Beef grilled patty, homemade buttered buns, caramelized onions, lettuce, tomatoes, 3 secret sauces",
        cs_dict.get("Premium Grilled Patties"),
        200,
        True,
        user,
    ),
    (
        "Cheese Burger",
        "100% Beef grilled patty, homemade buttered buns, bacon, caramelized onions, pickles, secret cheese sauce",
        cs_dict.get("Premium Grilled Patties"),
        195,
        True,
        user,
    ),
    (
        "BBQ Burger",
        "100% Beef grilled patty, homemade buttered buns, onion rings, homemade bbq sauce",
        cs_dict.get("Premium Grilled Patties"),
        195,
        True,
        user,
    ),
    (
        "Juicy Weekend",
        "A premium burger with bacon jam, crispy bacon bits, secret saucewith american cheese slice on top and a surprise cheese inside the patty!",
        cs_dict.get("Premium Grilled Patties"),
        250,
        True,
        user,
    ),
    (
        "Chicken Cheese Bomb",
        "Crispy cchicken patty in hot and honey coating, with fried mozarella for a perfect cheese pull! *consume while it's still hot*",
        cs_dict.get("Chicken Burgers"),
        235,
        True,
        user,
    ),
    (
        "Hot and Honey",
        "Our take on the famous weet and spicy chicken burger with fresh coleslaw. It's tangy, juicy, fresh, and crispy!",
        cs_dict.get("Chicken Burgers"),
        195,
        True,
        user,
    ),
    (
        "Classic Smash",
        "Smashed beef patty, caramelized onions, smash sauce, and cheddar cheese slice",
        cs_dict.get("Smash Burgers"),
        120,
        True,
        user,
    ),
    (
        "Breakfast Smash",
        "Smashed beef patty, bacon, egg, smash sauce, caramelized onions, and cheddar cheese slice",
        cs_dict.get("Smash Burgers"),
        145,
        True,
        user,
    ),
    (
        "BBQ Smash",
        "Smashed beef patty, homemade BBQ sauce, smash sauce, caramelized onions, and cheddar cheese slice",
        cs_dict.get("Smash Burgers"),
        130,
        True,
        user,
    ),
    (
        "Chili Smash",
        "Smashed beef patty, grilled green chili, smash sauce, caramelized onions, and cheddar cheese slice",
        cs_dict.get("Smash Burgers"),
        130,
        True,
        user,
    ),
    (
        "Weekender Ultra-Smashed",
        "4pcs smashed beef patty, 4pcs cheddar cheese slices, smash sauce, caramelized onions, and mozarella on top",
        cs_dict.get("Smash Burgers"),
        350,
        True,
        user,
    ),
    ("Cheddar cheese slice", "Bonus cheddar cheese", cs_dict.get("Add-ons"), 25, True, user),
    ("Beef patty", "Bonus patty", cs_dict.get("Add-ons"), 45, True, user),
    ("Sunny side up egg", "Bonus egg", cs_dict.get("Add-ons"), 20, True, user),
    ("Bacon", "Bonus bacon", cs_dict.get("Add-ons"), 40, True, user),
    (
        "Chicken and Pancake",
        "Homemade pancake with syrup and fried chicken breast on top",
        cs_dict.get("Pancakes"),
        155,
        True,
        user,
    ),
    (
        "Breakfast Pancake",
        "Homemade pancake with syrup, egg, and bacon on top",
        cs_dict.get("Pancakes"),
        145,
        True,
        user,
    ),
    (
        "Basic Pancake",
        "Homemade pancake with syrup",
        cs_dict.get("Pancakes"),
        85,
        True,
        user,
    ),
    (
        "Oreo Pancake",
        "Homemade pancake with syrup topped with homemade oreo ganache",
        cs_dict.get("Pancakes"),
        149,
        True,
        user,
    ),
    (
        "Choco Nutty Pancake",
        "Homemade pancake with homemade choco nut ganache on top",
        cs_dict.get("Pancakes"),
        140,
        True,
        user,
    ),
    (
        "BlueBerry Pancake",
        "Homemade pancake with blueberry compote on top",
        cs_dict.get("Pancakes"),
        150,
        True,
        user,
    ),
    (
        "Mini Pancakes",
        "8 pieces mini pancakes with syrup",
        cs_dict.get("Pancakes"),
        100,
        True,
        user,
    ),
    (
        "Kung Pao Fried Rice",
        "A spicy, stir-fried Chinese dish made with cubes of chicken, peanuts, vegetables, and chili peppers",
        cs_dict.get("Rice Meals"),
        105,
        True,
        user,
    ),
    (
        "Kimchi Fried Rice",
        "Our very own version of the famous kimchi fried rice with korean spam, sunny side up egg, seaweed, and mozarella cheese",
        cs_dict.get("Rice Meals"),
        130,
        True,
        user,
    ),
    (
        "Beef Chao Fan",
        "Stir-fried rice that is mixed with ground beef, pieces of vegetables, and eggs",
        cs_dict.get("Rice Meals"),
        105,
        True,
        user,
    ),
    (
        "Kung Pao Noods",
        "A spicy, stir-fried noodles with cubes of chicken, peanuts, vegetables, and eggs",
        cs_dict.get("Rice Meals"),
        105,
        True,
        user,
    ),
    (
        "Homemade Parmesan Fries",
        "Fresh potatoes fried to perfection, topped with parsley and parmesan cheese",
        cs_dict.get("Sides"),
        65,
        True,
        user,
    ),
    (
        "Beer-battered Onion Rings",
        "Beer-battered white onions fried to perfection! Comes with a special mayo dip",
        cs_dict.get("Sides"),
        125,
        True,
        user,
    ),
    (
        "Cheesy Bacon Fries",
        "Fresh potatoes fried to perfection, topped with cheesy sauce, crispy bacon, and parsley",
        cs_dict.get("Sides"),
        110,
        True,
        user,
    ),
    (
        "Soy Honey Wings",
        "6 pcs crispy and tasty chicken wings with homemade soy honey sauce",
        cs_dict.get("Sides"),
        290,
        True,
        user,
    ),
    (
        "Buffalo Wings",
        "6 pcs crispy and tasty chicken wings with homemade orginal buffalo sauce",
        cs_dict.get("Sides"),
        290,
        True,
        user,
    ),
    (
        "Garlic Parmesan Wings",
        "6 pcs crispy and tasty chicken wings with homemade garlic parmesan sauce",
        cs_dict.get("Sides"),
        290,
        True,
        user,
    ),
    (
        "Dream Nachos",
        "4 layer nachos dip with tortilla chips. Dip consists of beef, salsa, cheese, and more cheese!",
        cs_dict.get("Sides"),
        235,
        True,
        user,
    ),
    (
        "Extra Chips (Nachos)",
        "Bonus nacho chips",
        cs_dict.get("Sides"),
        60,
        True,
        user,
    ),
    (
        "Cheese Dunk Sauce",
        "Cheesy sauce that's perfect for a burger, fries or wings dip!",
        cs_dict.get("Sides"),
        50,
        True,
        user,
    ),
    (
        "Milkshake",
        "Refreshing original homemade milkshake with chocolate fudge and chocolate ice cream",
        cs_dict.get("Drinks"),
        125,
        True,
        user,
    ),
]
for item in product_values:
    Product.objects.create(**dict(zip(product_fields, item)))
