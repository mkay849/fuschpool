from datetime import datetime
from typing import Dict, List, Tuple
from pytz import timezone

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.aggregates import Count

from core.models import PickPoolUser
from nfl.defines import (
    CityChoices,
    PickChoices,
    SeasonType,
    StadiumChoices,
    TeamChoices,
)

est_tz = timezone("EST")


class DateRangeMixin(models.Model):
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()

    class Meta:
        abstract = True


class Team(models.Model):
    id = models.PositiveSmallIntegerField(choices=TeamChoices.choices, primary_key=True)
    city = models.CharField(max_length=3, choices=CityChoices.choices)
    stadium = models.CharField(max_length=4, choices=StadiumChoices.choices)

    @property
    def abbreviation(self) -> str:
        return TeamChoices(self.id).name

    @property
    def full_name(self) -> str:
        return TeamChoices(self.id).label

    @property
    def short_name(self) -> str:
        if " " in self.full_name:
            return self.full_name.rsplit(" ", 1)[1]
        return self.full_name

    @property
    def standings(self) -> Tuple[int, int, int]:
        cur_date = datetime.now(timezone("UTC"))
        cur_week = (
            Week.objects.select_related("year")
            .filter(start_timestamp__lte=cur_date, end_timestamp__gt=cur_date)
            .first()
        )
        season_games = Game.objects.filter(
            Q(home_team=self.id) | Q(visitor_team=self.id),
            final=True,
            week__year__value=cur_week.year.value,
            week__value__lte=cur_week.value,
        )
        cur_season_type = cur_week.season_type
        if cur_season_type == SeasonType.REGULAR:
            season_games = season_games.exclude(week__value__lt=5)
        elif cur_season_type == SeasonType.POST:
            season_games = season_games.exclude(week__value__lt=23)
        elif cur_season_type == SeasonType.OFF:
            pass
        res = season_games.aggregate(
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
        return res.get("won", 0), res.get("lost", 0), res.get("tie", 0)

    def __str__(self) -> str:
        return self.full_name


class YearManager(models.Manager):
    def evaluate_year(self, year: int) -> List[Tuple[int, List[PickPoolUser]]]:
        """Evaluate a whole season.

        Parameters
        ----------
        year : int
            Year to evaluate

        Returns
        -------
        List[Tuple[int, List[PickPoolUser]]]
            List of tuples containing earned points with corresponding users.
        """
        try:
            cur_year = self.get(year=year)
        except Year.DoesNotExist:
            pass
        return []


class Year(DateRangeMixin):
    value = models.PositiveSmallIntegerField(unique=True)

    def __str__(self) -> str:
        return f"Year: {self.value}"


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
                    if pick.user in user_points:
                        user_points[pick.user] += points
                    else:
                        user_points[pick.user] = points

            res = {}
            for user, points in user_points.items():
                if points in res:
                    res[points].append(user)
                else:
                    res[points] = [user]
            return sorted(res.items(), reverse=True)
        except Week.DoesNotExist:
            return []


class Week(DateRangeMixin):
    class Meta:
        unique_together = ["year", "value"]

    value = models.PositiveSmallIntegerField()
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    objects = WeekManager()

    @property
    def season_type(self) -> int:
        if self.value == 1:
            season_type = SeasonType.PRE  # Hall of Fame Week
        elif 1 < self.value < 5:
            season_type = SeasonType.PRE
        elif 4 < self.value < 23:
            season_type = SeasonType.REGULAR
        elif self.value == 23:
            season_type = SeasonType.POST  # Wild Card Weekend
        elif self.value == 24:
            season_type = SeasonType.POST  # Divisional Playoffs
        elif self.value == 25:
            season_type = SeasonType.POST  # Conference Championships
        elif self.value == 26:
            season_type = SeasonType.POST  # Pro Bowl
        elif self.value == 27:
            season_type = SeasonType.POST  # Super Bowl
        else:
            season_type = SeasonType.OFF
        return season_type

    @property
    def nfl_week(self) -> int:
        if self.value < 5:
            return self.value
        elif 4 < self.value < 23:
            return self.value - 4
        elif 22 < self.value < 28:
            return self.value - 22
        else:
            return self.value - 27

    def __str__(self) -> str:
        return f"Week: {self.value}, {self.year}"


class Game(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="games")
    timestamp = models.DateTimeField()
    event_id = models.PositiveIntegerField()
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
