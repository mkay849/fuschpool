from datetime import date
from typing import Dict, List, Tuple

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.aggregates import Count
from pytz import timezone

from core.models import PickPoolUser
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


class WeekManager(models.Manager):
    def evaluate_week(
        self, year: int, week: int
    ) -> List[Tuple[int, List[PickPoolUser]]]:
        """Evaluate a whole week.

        Parameters
        ----------
        models : WeekManager
            Django model manager
        year : int
            Year to evaluate
        week : int
            Week to evaluate

        Returns
        -------
        List[Tuple[int, List[PickPoolUser]]]
            List of tuples containing earned points with corresponding users.
        """
        try:
            cur_week = self.get(year__year=year, week=week)
            user_points = {}
            for game in cur_week.games.all():
                game_points = game.evaluate_game()
                for pick, points in game_points.items():
                    if pick in user_points:
                        user_points[pick.user] += points
                    else:
                        user_points[pick.user] = points

            res = {}
            for user, points in user_points.items():
                if points in res:
                    res[points].append(user)
                else:
                    res[points] = [user]
            return sorted(res, reverse=True)
        except Week.DoesNotExist:
            return {}


class Week(models.Model):
    class Meta:
        unique_together = ["year", "week"]

    week = models.PositiveSmallIntegerField()
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    objects = WeekManager()

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
        """Determine the winner team of this game.

        Returns
        -------
        PickChoices
            If this game is final returns the winning team or tie.
        """
        if not self.final:
            return None
        if self.home_team_score == self.visitor_team_score:
            return PickChoices.TIED_GAME
        if self.home_team_score > self.visitor_team_score:
            return PickChoices.HOME_TEAM
        return PickChoices.VISITOR_TEAM

    def evaluate_game(self) -> Dict["Pick", int]:
        """Evaluate all picks of a game.

        Returns:
            Dict[int, List[Pick]]
                Mapping of picks with their corresponding points earned.
        """
        user_points = {}
        for pick in self.picks.all():
            user_points[pick] = pick.awarded_points
        return user_points

    def is_monday_night(self) -> bool:
        """Check if this game is a monday night game.

        Returns
        -------
        bool
            True if this game is a monday night game, False otherwise.
        """
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
    picked_tie_break = models.PositiveSmallIntegerField(default=0)

    @property
    def awarded_points(self) -> int:
        """This pick's points earned

        Returns
        -------
        int
            Points earned, if any
        """
        if self.selection == self.game.winner:
            return 1
        return 0

    @property
    def tie_break(self) -> int:
        """This pick's tie break after the game has finished.

        Returns
        -------
        int
            This pick's tie break.
        """
        if not self.game.final:
            return None
        tb = abs(self.game.home_team_score - self.game.visitor_team_score)
        game_winner = self.game.winner
        if self.selection == game_winner:
            return abs(tb - self.picked_tie_break)
        else:
            if game_winner == PickChoices.HOME_TEAM:
                return self.game.home_team_score + self.picked_tie_break
            elif game_winner == PickChoices.VISITOR_TEAM:
                return self.game.visitor_team_score + self.picked_tie_break
        return self.picked_tie_break

    def __str__(self) -> str:
        return f"{self.user.first_name} picked '{PickChoices(self.selection).label}' for {self.game}"
