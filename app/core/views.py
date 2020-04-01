from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import FormView


class LoginView(FormView):
    form_class = AuthenticationForm
    success_url = '/nfl/'
    template_name = 'core/index.html'

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.session.get('user'):
            return redirect('overview')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class LogoutView(RedirectView):
    url = '/login/'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class OverviewView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'core/index.html'


class ProfileView(LoginRequiredMixin, RedirectView):
    login_url = 'login'
    url = '/nfl/'
