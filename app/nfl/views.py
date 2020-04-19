from datetime import date
from typing import Tuple

from django.db.models import F, Q
from django.db.models.aggregates import Count, Max, Sum
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from django.views.generic import ListView, TemplateView

from nfl.defines import CityChoices, StadiumChoices, TeamChoices
from nfl.models import Game, Pick, Team, Week, Year


class SeasonWeekMixin(object):
    @staticmethod
    def _get_real_week(nfl_week: int) -> Tuple[int, str]:
        if nfl_week is None:
            return None, None
        cur_week = nfl_week
        if nfl_week == 1:
            season_type = "Hall of Fame Week"
        elif 1 < nfl_week < 6:
            season_type = "Preseason"
            cur_week = nfl_week - 1
        elif 5 < nfl_week < 23:
            season_type = "Regular Season"
            cur_week = nfl_week - 5
        elif nfl_week == 23:
            season_type = "Wild Card Weekend"
        elif cur_week == 24:
            season_type = "Divisional Playoffs"
        elif nfl_week == 25:
            season_type = "Conference Championships"
        elif nfl_week == 26:
            season_type = "Pro Bowl"
        else:
            season_type = "Super Bowl"
        return cur_week, season_type

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "season" in kwargs:
            cur_season = kwargs.get("season")
        else:
            now = date.today()
            cur_season = now.year if now.month > 8 else now.year - 1

        if "week" in kwargs:
            nfl_week = kwargs.get("week")
        else:
            nfl_week = (
                Game.objects.filter(final=True, week__year__year=cur_season,)
                .aggregate(cur_week=Max("week"),)
                .get("cur_week")
                or 1
            )

        real_week, season_type = SeasonWeekMixin._get_real_week(nfl_week)
        context.update(
            {
                "season": cur_season,
                "nfl_week": nfl_week,
                "week": real_week,
                "season_type": season_type,
            }
        )
        return context


class SeasonGamesMixin(SeasonWeekMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["season_games"] = Game.objects.filter(
            final=True,
            week__year__year=context["season"],
            week__week__lte=context["nfl_week"],
        )
        return context


class TeamsMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = Team.objects.exclude(
            abbr__in=(TeamChoices.AFC, TeamChoices.NFC)
        )
        return context


class SeasonStandingsMixin(SeasonGamesMixin, TeamsMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        verbose_teams = []
        for team in context["teams"]:
            season_team_games = context.get("season_games").filter(
                Q(home_team=team.id) | Q(visitor_team=team.id),
            )
            season_game_agg = season_team_games.aggregate(
                won=Count(
                    "id",
                    filter=Q(
                        home_team=team.id, home_team_score__gt=F("visitor_team_score")
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
                        home_team=team.id, home_team_score__lt=F("visitor_team_score"),
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


class ScheduleView(SeasonStandingsMixin, TemplateView):
    template_name = "nfl/schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_games = Game.objects.filter(
            week__year__year=context.get("season"), week=context.get("nfl_week") + 1,
        )
        context["next_games"] = next_games
        return context


class StandingsView(SeasonWeekMixin, TemplateView):
    template_name = "nfl/standings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"standings": None})
        return context


class TeamsView(SeasonPointsMixin, TemplateView):
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


class PicksView(SeasonWeekMixin, ListView):
    context_object_name = "picks"
    model = Pick
    template_name = "nfl/picks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.context_object_name in context:
            picks = context.get(self.context_object_name)
            new_picks = {}
            for pick in picks:
                if pick.user in new_picks:
                    new_picks[pick.user].append(pick)
                else:
                    new_picks[pick.user] = [pick]
            context[self.context_object_name] = new_picks
            context["games"] = self.latest_games
        return context

    def get_queryset(self):
        now_ts = now()
        try:
            if "season" in self.kwargs:
                cur_season = self.kwargs.get("season")
            else:
                cur_season = Year.objects.aggregate(cur_season=Max("year")).get(
                    "cur_season",
                )

            if "week" in self.kwargs:
                cur_week = self.kwargs.get("week")
            else:
                cur_week = (
                    Week.objects.filter(year__year=cur_season)
                    .aggregate(cur_week=Max("week"))
                    .get("cur_week")
                )

            self.latest_games = Game.objects.filter(
                week__year__year=cur_season, week__week=cur_week
            ).order_by("timestamp", "home_team")
            if self.latest_games.exists():
                cur_picks = Pick.objects.filter(game__in=self.latest_games,)
                if now_ts < self.latest_games.last().timestamp:
                    if (
                        cur_picks.filter(
                            user=self.resquest.user, game__timestamp__lte=now_ts
                        ).count()
                        == self.latest_games.filter(timestamp__lte=now_ts).count()
                    ):
                        cur_picks = cur_picks.filter(game__timestamp__lte=now_ts)
                return cur_picks.order_by(
                    "user__first_name", "game__timestamp", "game__home_team",
                )
        except Game.DoesNotExist:
            pass
        except Pick.DoesNotExist:
            pass
        except Year.DoesNotExist:
            pass
        return Pick.objects.none()
