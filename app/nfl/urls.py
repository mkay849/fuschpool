from django.urls import path

from nfl.views import ScheduleView, StandingsView, TeamsView, PicksView

app_name = "nfl"
urlpatterns = [
    path("", StandingsView.as_view(), name="standings"),
    path("<int:season>/<int:week>/", StandingsView.as_view(), name="standings-week"),
    path("teams/", TeamsView.as_view(), name="teams"),
    path("teams/<int:season>/<int:week>/", TeamsView.as_view(), name="teams-week"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path(
        "schedule/<int:season>/<int:week>/",
        ScheduleView.as_view(),
        name="schedule-week",
    ),
    path("picks/", PicksView.as_view(), name="picks"),
    path("picks/<int:season>/<int:week>/", PicksView.as_view(), name="picks-week"),
]
