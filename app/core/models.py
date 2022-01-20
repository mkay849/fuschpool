from typing import Dict

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q

from nfl.defines import PickChoices


class PickPoolUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)

    def standings(self, season: int) -> Dict[str, int]:
        season_picks = self.picks.filter(
            game__week__year__value=season, game__final=True
        )
        won = season_picks.filter(
            Q(
                game__visitor_team_score__gt=F("game__home_team_score"),
                selection=PickChoices.VISITOR_TEAM,
            )
            | Q(
                game__home_team_score__gt=F("game__visitor_team_score"),
                selection=PickChoices.HOME_TEAM,
            )
            | Q(
                game__visitor_team_score=F("game__home_team_score"),
                selection=PickChoices.TIED_GAME,
            )
        ).count()
        lost = season_picks.filter(
            Q(
                game__visitor_team_score__gt=F("game__home_team_score"),
                selection=PickChoices.HOME_TEAM,
            )
            | Q(
                game__home_team_score__gt=F("game__visitor_team_score"),
                selection=PickChoices.VISITOR_TEAM,
            )
        ).count()
        return {
            "won": won,
            "lost": lost,
            "won_lost_ratio": won / (won + lost) if won or lost else 0,
        }
