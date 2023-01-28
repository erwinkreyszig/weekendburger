from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

# create permissions
ct = ContentType.objects.get_for_model(User)
can_add_order_perm = Permission.objects.create(codename="can_add_orders", name="Can add orders", content_type=ct)
can_view_order_perm = Permission.objects.create(codename="can_view_orders", name="Can view orders", content_type=ct)
can_view_report_perm = Permission.objects.create(codename="can_view_reports", name="Can view reports", content_type=ct)

# create groups
add_order_group, _ = Group.objects.get_or_create(name="Add order group")
view_order_group, _ = Group.objects.get_or_create(name="View orders group")
view_report_group, _ = Group.objects.get_or_create(name="View reports group")
mgmt_group, _ = Group.objects.get_or_create(name="Managemnt")

# add permissions
add_order_group.permissions.add(can_add_order_perm)
add_order_group.permissions.add(can_view_order_perm)
view_order_group.permissions.add(can_view_order_perm)
view_report_group.permissions.add(can_view_report_perm)
for perm in (can_add_order_perm, can_view_order_perm, can_view_report_perm):
    mgmt_group.permissions.add(perm)
