from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect


class CoreLoginView(LoginView):
    # Template interno (LIMS)
    template_name = "internal/registration/login.html"
    redirect_authenticated_user = True


def logout_user(request):
    logout(request)
    return redirect("login")
