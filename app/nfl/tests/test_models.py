import pytest

from nfl.defines import PickChoices, TeamChoices
from nfl.models import Team


@pytest.mark.django_db
class TestGameModel:
    def test_string(self, nfl_game):
        assert (
            str(nfl_game)
            == "Cincinnati Bengals at Chicago Bears on 2019-08-08 23:00:00+00:00"
        )

    def test_properties(self, nfl_game):
        assert nfl_game.winner is None

        nfl_game.final = True
        nfl_game.home_team_score = 23
        nfl_game.visitor_team_score = 23
        assert nfl_game.winner == PickChoices.TIED_GAME

        nfl_game.home_team_score = 42
        assert nfl_game.winner == PickChoices.HOME_TEAM

        nfl_game.home_team_score = 17
        assert nfl_game.winner == PickChoices.VISITOR_TEAM

    def test_is_monday_night(self, nfl_game):
        assert not nfl_game.is_monday_night()

        nfl_game.timestamp = nfl_game.timestamp.replace(day=12)
        assert nfl_game.is_monday_night()


@pytest.mark.django_db
class TestTeamModel:
    def test_full_name(self):
        cur_team = Team.objects.get(abbr="CHI")
        assert cur_team.full_name == TeamChoices("CHI").label
        cur_team = Team.objects.get(abbr="TB")
        assert cur_team.full_name == TeamChoices("TB").label

    def test_short_name(self):
        cur_team = Team.objects.get(abbr="CHI")
        assert cur_team.short_name == "Bears"
        cur_team = Team.objects.get(abbr="TB")
        assert cur_team.short_name == "Buccaneers"

    def test_string(self):
        cur_team = Team.objects.get(abbr="CHI")
        assert str(cur_team) == "Chicago Bears"


@pytest.mark.django_db
class TestPickModel:
    def test_string(self, pick):
        assert (
            str(pick)
            == "Name 1 picked 'Home Team' for Cincinnati Bengals at Chicago Bears on 2019-08-08 23:00:00+00:00"
        )

    def test_awarded_points(self, pick):
        pick.game.final = True
        pick.game.home_team_score = 23
        pick.game.visitor_team_score = 27
        assert pick.awarded_points == 0

        pick.game.home_team_score = 28
        assert pick.awarded_points == 1
