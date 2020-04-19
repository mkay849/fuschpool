from datetime import datetime
from pathlib import Path

import pytest
from django.conf import settings
from pytz import utc
from yaml import safe_load

from nfl.models import Game, Team

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@pytest.fixture
def nfl_game(make_nfl_game):
    """Fixture creating a nfl game."""
    return make_nfl_game()


@pytest.fixture
def make_nfl_game(week):
    """Factory fixture to create nfl games."""

    def _make_nfl_game(**kwargs):
        home_team = kwargs.get("home_team", Team.objects.get(pk=1))
        visitor_team = kwargs.get("visitor_team", Team.objects.get(pk=2))
        return Game.objects.get_or_create(
            week=week,
            timestamp=kwargs.get("timestamp", datetime(2019, 8, 8, 23, tzinfo=utc)),
            home_team=home_team,
            visitor_team=visitor_team,
        )[0]

    return _make_nfl_game


@pytest.fixture
def nfl_games(make_nfl_game, make_week, **kwargs):
    """Fixture creating all games of a nfl week."""
    cur_week = kwargs.get("week", make_week())
    fixture = Path(settings.BASE_DIR) / "nfl/fixtures/nfl_s2019.yaml"
    with fixture.open("r") as yaml_file:
        data = safe_load(yaml_file)
        for game in data:
            game_data = game["fields"]
            if game_data["week"] == cur_week.week:
                make_nfl_game(
                    week=cur_week,
                    home_team=Team.objects.get(pk=game_data.get("home_team")),
                    home_team_score=game_data.get("home_team_score"),
                    visitor_team=Team.objects.get(pk=game_data.get("visitor_team")),
                    visitor_team_score=game_data.get("visitor_team_score"),
                    final=game_data.get("final"),
                )
    return Game.objects.all()
