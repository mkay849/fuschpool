from datetime import date
from typing import Tuple

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.aggregates import Count
from pytz import timezone

from nfl.defines import CityChoices, PickChoices, StadiumChoices, TeamChoices

est_tz = timezone("EST")


class Team(models.Model):
    city = models.CharField(
        max_length=3, choices=CityChoices.choices, default=CityChoices.ATLANTA
    )
    abbr = models.CharField(
        max_length=3, choices=TeamChoices.choices, default=TeamChoices.CARDINALS
    )
    stadium = models.CharField(
        max_length=4, choices=StadiumChoices.choices, default=StadiumChoices.AS
    )

    @property
    def full_name(self) -> str:
        return TeamChoices(self.abbr).label

    @property
    def short_name(self) -> str:
        return self.full_name.rsplit(" ", 1)[1]

    @property
    def standings(self) -> Tuple[int, int, int]:
        now = date.today()
        cur_season = now.year if now.month > 8 else now.year - 1
        res = Game.objects.filter(
            Q(home_team=self.id) | Q(visitor_team=self.id),
            final=True,
            week__year__year=cur_season,
        ).aggregate(
            won=Count(
                "id",
                filter=Q(
                    home_team=self.id, home_team_score__gt=F("visitor_team_score")
                ),
            )
            + Count(
                "id",
                filter=Q(
                    visitor_team=self.id, visitor_team_score__gt=F("home_team_score")
                ),
            ),
            lost=Count(
                "id",
                filter=Q(
                    home_team=self.id, home_team_score__lt=F("visitor_team_score"),
                ),
            )
            + Count(
                "id",
                filter=Q(
                    visitor_team=self.id, visitor_team_score__lt=F("home_team_score")
                ),
            ),
            tie=Count("id", filter=Q(home_team_score=F("visitor_team_score"))),
        )
        return res.get("won", 0), res.get("tie", 0), res.get("lost", 0)

    def __str__(self) -> str:
        return f"{TeamChoices(self.abbr).label}"


class Year(models.Model):
    year = models.PositiveSmallIntegerField(unique=True)

    def __str__(self) -> str:
        return f"Year: {self.year}"


class Week(models.Model):
    class Meta:
        unique_together = ["year", "week"]

    week = models.PositiveSmallIntegerField()
    year = models.ForeignKey(Year, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Week: {self.week}, {self.year}"


class Game(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="games")
    timestamp = models.DateTimeField()
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="home_teams"
    )
    home_team_score = models.PositiveSmallIntegerField(null=True, default=None)
    visitor_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="visitor_teams"
    )
    visitor_team_score = models.PositiveSmallIntegerField(null=True, default=None)
    final = models.BooleanField(default=False)

    @property
    def winner(self) -> PickChoices:
        if not self.final:
            return None
        if self.home_team_score == self.visitor_team_score:
            return PickChoices.TIED_GAME
        if self.home_team_score > self.visitor_team_score:
            return PickChoices.HOME_TEAM
        return PickChoices.VISITOR_TEAM

    def is_monday_night(self) -> bool:
        ts_est = self.timestamp.astimezone(est_tz)
        if ts_est.weekday() == 0:
            return True
        return False

    def __str__(self) -> str:
        return f"{self.visitor_team} at {self.home_team} on {self.timestamp}"


class Pick(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="picks"
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="picks")
    selection = models.SmallIntegerField(
        choices=PickChoices.choices, default=PickChoices.TBP
    )
    tie_break = models.PositiveSmallIntegerField(default=0)

    @property
    def awarded_points(self):
        if self.selection == self.game.winner:
            return 1
        return 0

    def __str__(self) -> str:
        return f"{self.user.first_name} picked '{PickChoices(self.selection).label}' for {self.game}"
