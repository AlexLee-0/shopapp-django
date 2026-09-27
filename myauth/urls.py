from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    MyLogoutView,
    AboutMeView,
    RegisterView,
)
from .forms import BootstrapAuthenticationForm

app_name = "myauth"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
            authentication_form=BootstrapAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),
]