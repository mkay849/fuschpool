from datetime import date, datetime, time, timezone
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import Coalesce
from django.views.generic import ListView, TemplateView

from nfl.defines import CityChoices, SeasonType, StadiumChoices, TeamChoices
from nfl.models import Game, Pick, Team, Week

logger = logging.getLogger(__name__)


class WeekMixin(object):
    week = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"week": self.week})
        return context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if "year" in kwargs and "month" in kwargs and "day" in kwargs:
            cur_date = datetime.combine(
                date(kwargs["year"], kwargs["month"], kwargs["day"]),
                time(9),
                tzinfo=timezone.utc,
            )
        else:
            cur_date = datetime.now(timezone.utc)
        self.week = (
            Week.objects.select_related("year")
            .filter(start_timestamp__lte=cur_date, end_timestamp__gt=cur_date)
            .first()
        )


class SeasonGamesMixin(WeekMixin):
    season_games = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        season_games = self.season_games
        cur_season_type = self.week.season_type if self.week else SeasonType.OFF
        if cur_season_type == SeasonType.REGULAR:
            season_games = season_games.exclude(week__value__lt=5)
        elif cur_season_type == SeasonType.POST:
            season_games = season_games.exclude(week__value__lt=23)
        elif cur_season_type == SeasonType.OFF:
            pass
        context["season_games"] = season_games
        return context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.week:
            self.season_games = Game.objects.filter(
                final=True,
                week__year__value=self.week.year.value,
                week__value__lte=self.week.value,
            )


class WeekGamesMixin(WeekMixin):
    week_games = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["week_games"] = self.week_games
        return context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.week:
            self.week_games = Game.objects.filter(week=self.week).order_by(
                "timestamp", "home_team"
            )


class TeamsMixin(object):
    teams = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = self.teams
        return context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.teams = Team.objects.exclude(id__in=(TeamChoices.AFC, TeamChoices.NFC))


class SeasonStandingsMixin(SeasonGamesMixin, TeamsMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        verbose_teams = []
        if self.teams and self.season_games:
            for team in self.teams:
                season_team_games = self.season_games.filter(
                    Q(home_team=team.id) | Q(visitor_team=team.id),
                )
                season_game_agg = season_team_games.aggregate(
                    won=Count(
                        "id",
                        filter=Q(
                            home_team=team.id,
                            home_team_score__gt=F("visitor_team_score"),
                        ),
                    )
                    + Count(
                        "id",
                        filter=Q(
                            visitor_team=team.id,
                            visitor_team_score__gt=F("home_team_score"),
                        ),
                    ),
                    lost=Count(
                        "id",
                        filter=Q(
                            home_team=team.id,
                            home_team_score__lt=F("visitor_team_score"),
                        ),
                    )
                    + Count(
                        "id",
                        filter=Q(
                            visitor_team=team.id,
                            visitor_team_score__lt=F("home_team_score"),
                        ),
                    ),
                    tie=Count("id", filter=Q(home_team_score=F("visitor_team_score"))),
                )
                if season_game_agg.get("won") or season_game_agg.get("lost"):
                    won_lost_ratio = 1 - season_game_agg.get("lost") / float(
                        season_game_agg.get("won") + season_game_agg.get("lost")
                    )
                else:
                    won_lost_ratio = 0
                verbose_teams.append(
                    {
                        "db_team": team,
                        "city": CityChoices(team.city).label,
                        "stadium": StadiumChoices(team.stadium).label,
                        "won": season_game_agg.get("won") or 0,
                        "lost": season_game_agg.get("lost") or 0,
                        "tie": season_game_agg.get("tie") or 0,
                        "won_lost_ratio": won_lost_ratio,
                    }
                )
        context.update(
            {
                "verbose_teams": sorted(
                    verbose_teams,
                    key=lambda i: (i["won"], i["tie"], i["lost"]),
                    reverse=True,
                ),
            }
        )
        return context


class SeasonPointsMixin(SeasonStandingsMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for team in context.get("verbose_teams"):
            season_team_games = context.get("season_games").filter(
                Q(home_team=team.get("db_team").id)
                | Q(visitor_team=team.get("db_team").id),
            )
            season_game_agg = season_team_games.aggregate(
                points_for=Coalesce(
                    Sum(
                        "home_team_score",
                        filter=Q(
                            home_team=team.get("db_team").id,
                            home_team_score__gt=F("visitor_team_score"),
                        ),
                    ),
                    0,
                )
                + Coalesce(
                    Sum(
                        "visitor_team_score",
                        filter=Q(
                            visitor_team=team.get("db_team").id,
                            visitor_team_score__gt=F("home_team_score"),
                        ),
                    ),
                    0,
                ),
                points_against=Coalesce(
                    Sum(
                        "visitor_team_score",
                        filter=Q(
                            home_team=team.get("db_team").id,
                            home_team_score__lt=F("visitor_team_score"),
                        ),
                    ),
                    0,
                )
                + Coalesce(
                    Sum(
                        "home_team_score",
                        filter=Q(
                            visitor_team=team.get("db_team").id,
                            visitor_team_score__lt=F("home_team_score"),
                        ),
                    ),
                    0,
                ),
            )
            if season_game_agg.get("points_for") or season_game_agg.get(
                "points_against"
            ):
                points_diff = season_game_agg.get(
                    "points_for", 0
                ) - season_game_agg.get("points_against", 0)
            else:
                points_diff = 0
            team.update(
                {
                    "points_for": season_game_agg.get("points_for") or 0,
                    "points_against": season_game_agg.get("points_against") or 0,
                    "points_diff": points_diff,
                }
            )
        context.update(
            {
                "verbose_teams": sorted(
                    context["verbose_teams"],
                    key=lambda i: (i["points_diff"]),
                    reverse=True,
                ),
            }
        )
        return context


class ScheduleView(WeekGamesMixin, TemplateView):
    template_name = "nfl/schedule.html"


class StandingsView(LoginRequiredMixin, WeekMixin, TemplateView):
    login_url = "/login/"
    template_name = "nfl/standings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"standings": None})
        return context


class TeamsView(LoginRequiredMixin, SeasonPointsMixin, TemplateView):
    login_url = "/login/"
    template_name = "nfl/teams.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "verbose_teams": sorted(
                    context.get("verbose_teams"),
                    key=lambda i: (i["points_diff"]),
                    reverse=True,
                ),
            }
        )
        return context


class PicksView(LoginRequiredMixin, WeekGamesMixin, ListView):
    context_object_name = "picks"
    login_url = "/login/"
    model = Pick
    template_name = "nfl/picks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.week_games and self.context_object_name in context:
            picks = context.get(self.context_object_name)
            user_picks = picks.filter(user=self.request.user)
            picked_games = [pick.game for pick in user_picks]
            now_dt = datetime.now(timezone.utc)
            missed_games = list(
                self.week_games.filter(timestamp__lte=now_dt).exclude(
                    id__in=[g.id for g in picked_games]
                )
            )
            overview_games = picked_games + missed_games
            unpicked_games = list(
                self.week_games.exclude(Q(id__in=[g.id for g in overview_games]))
            )
            new_picks = {}
            for pick in picks:
                try:
                    new_picks[pick.user].append(pick)
                except KeyError:
                    new_picks[pick.user] = [pick]
            if len(missed_games) or len(unpicked_games):
                for idx, game in enumerate(self.week_games):
                    if game in unpicked_games:
                        for picks in new_picks.values():
                            picks.insert(idx, None)
                    elif game in missed_games:
                        for picks in new_picks.values():
                            picks.insert(
                                idx,
                                "missed"
                                if picks[0].user == self.request.user
                                else None,
                            )
            context[self.context_object_name] = new_picks
            context["unpicked_games"] = unpicked_games
        return context

    def get_queryset(self):
        try:
            if self.week_games and self.week_games.exists():
                return Pick.objects.filter(game__in=self.week_games).order_by(
                    "user__first_name", "game__timestamp", "game__home_team",
                )
        except Pick.DoesNotExist:
            pass
        return Pick.objects.none()

    def post(self, request, *args, **kwargs):
        picks = []
        for k, v in request.POST.items():
            if k[:4] != "pick":
                continue
            game_id = k.split("_")[1]
            tie_break = 0
            try:
                pick_choice, tie_break = v.split("_")
            except ValueError:
                pick_choice = v
            try:
                game = Game.objects.get(id=game_id)
            except Game.DoesNotExist:
                logger.warning(f"Unknown game_id={game_id}")
                continue
            picks.append(
                Pick(
                    user=request.user,
                    game=game,
                    selection=pick_choice,
                    picked_tie_break=tie_break,
                )
            )
        if len(picks):
            Pick.objects.bulk_create(picks)
        return self.get(request, *args, **kwargs)
