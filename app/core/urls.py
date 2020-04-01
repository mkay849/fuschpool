from django.urls import path

from core.views import LoginView, LogoutView, OverviewView, ProfileView

app_name = 'core'
urlpatterns = [
    path('', OverviewView.as_view(), name="overview"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile')
]
