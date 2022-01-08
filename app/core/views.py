from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import FormView

from .forms import ProfileForm


class LoginView(FormView):
    form_class = AuthenticationForm
    success_url = "/nfl/"
    template_name = "core/index.html"

    @method_decorator(sensitive_post_parameters("password"))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.session.get("user"):
            return redirect("nfl:standings")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.kwargs:
            return self.request.POST["next"]
        return self.success_url


class LogoutView(RedirectView):
    url = "/login/"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class OverviewView(LoginRequiredMixin, TemplateView):
    login_url = "/login/"
    template_name = "core/index.html"

    def get(self, request):
        return redirect("/nfl/")


class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = "/login/"
    url = "/profile/"
    template_name = "core/profile.html"

    def get(self, request):
        form = ProfileForm(user=request.user)
        return render(request, "core/profile.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST, user=request.user)
        if form.is_valid():
            updated_fields = []
            if first_name := form.cleaned_data.get("first_name"):
                if not request.user.first_name or request.user.first_name != first_name:
                    request.user.first_name = first_name
                    updated_fields.append("first_name")
            if last_name := form.cleaned_data.get("last_name"):
                if not request.user.last_name or request.user.last_name != last_name:
                    request.user.last_name = last_name
                    updated_fields.append("last_name")
            if email := form.cleaned_data.get("email"):
                if request.user.email != email:
                    request.user.email = email
                    updated_fields.append("email")
            if bd := form.cleaned_data.get("birth_date"):
                if not request.user.birth_date or request.user.birth_date != bd:
                    request.user.birth_date = bd
                    updated_fields.append("birth_date")
            if new_pw := form.cleaned_data.get("new_password_1"):
                request.user.set_password(new_pw)
                updated_fields.append("password")
            if len(updated_fields):
                request.user.save(update_fields=updated_fields)
            return redirect("/nfl/")
        return render(request, "core/profile.html", {"form": form})
