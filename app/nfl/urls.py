from django.urls import path

from nfl.views import ScheduleView, StandingsView, TeamsView, PicksView

app_name = "nfl"
urlpatterns = [
    path("", StandingsView.as_view(), name="standings"),
    path("teams/", TeamsView.as_view(), name="teams",),
    path("teams/<int:season>/", TeamsView.as_view(), name="teams",),
    path("teams/<int:season>/<int:week>/", TeamsView.as_view(), name="teams",),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("picks/", PicksView.as_view(), name="make_picks"),
]
