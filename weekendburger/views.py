from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import LoginForm
from orders.permissions import CAN_ADD_ORDER_PERM, CAN_VIEW_ORDER_PERM


class CustomLoginView(LoginView):
    template_name = "login.html"
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/orders/")
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(username=username, password=password)
        if not user:
            return render(request, self.template_name, {"form": form})
        login(request, user)
        if user.groups.filter(name="Add order group").count() > 0 and CAN_ADD_ORDER_PERM in user.get_all_permissions():
            return HttpResponseRedirect("/orders/new/")
        if user.groups.filter(name="Managemnt").count() > 0 or CAN_VIEW_ORDER_PERM in user.get_all_permissions():
            return HttpResponseRedirect("/orders/")


def logout_view(request):  # change to class based view?
    logout(request)
    return HttpResponseRedirect("/login/")
