from django.urls import path

from nfl.views import ScheduleView, StandingsView, TeamsView, PicksView

app_name = "nfl"
urlpatterns = [
    path("", StandingsView.as_view(), name="standings"),
    path("teams/", TeamsView.as_view(), name="teams",),
    path(
        "teams/<int:year>/<int:month>/<int:day>/",
        TeamsView.as_view(),
        name="teams-season",
    ),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("picks/", PicksView.as_view(), name="picks"),
    path(
        "picks/<int:year>/<int:month>/<int:day>/",
        PicksView.as_view(),
        name="picks-date",
    ),
]
