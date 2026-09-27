from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import BootstrapUserCreationForm
from .models import Profile


class AboutMeView(LoginRequiredMixin, UpdateView):
    """Показывает и обновляет профиль текущего пользователя (avatar + bio)."""
    model = Profile
    fields = ("avatar", "bio")
    template_name = "myauth/about-me.html"
    success_url = reverse_lazy("myauth:about-me")

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class RegisterView(CreateView):
    form_class = BootstrapUserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")