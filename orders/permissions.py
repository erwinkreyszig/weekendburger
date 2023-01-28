from django.core.exceptions import PermissionDenied

CAN_ADD_ORDER_PERM = "auth.can_add_orders"
CAN_VIEW_ORDER_PERM = "auth.can_view_orders"
CAN_VIEW_REPORT_PERM = "auth.can_view_reports"


def user_can_do(permissions=None):
    def user_is_allowed(function):
        def wrap(request, *args, **kwargs):
            for permission in permissions:
                if permission in request.user.get_all_permissions():
                    return function(request, *args, **kwargs)
            raise PermissionDenied

        return wrap

    return user_is_allowed
