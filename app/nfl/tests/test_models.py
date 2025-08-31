import pytest
from nfl.defines import PickChoices, TeamChoices
from nfl.models import Game, Team, Week


@pytest.mark.django_db
class TestGameModel:
    def test_string(self, nfl_game):
        assert str(nfl_game) == (
            "Buffalo Bills at Atlanta Falcons on 2019-08-08 23:00:00+00:00"
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

    def test_evaluate_game(self, make_pick, make_pick_pool_user, nfl_game):
        user1 = make_pick_pool_user()
        user2 = make_pick_pool_user()
        user3 = make_pick_pool_user()
        p1 = make_pick(
            game=nfl_game,
            user=user1,
        )
        p2 = make_pick(
            game=nfl_game,
            selection=PickChoices.VISITOR_TEAM,
            user=user2,
        )
        p3 = make_pick(
            game=nfl_game,
            selection=PickChoices.TIED_GAME,
            user=user3,
        )
        nfl_game.home_team_score = 23
        nfl_game.visitor_team_score = 27

        # Game is not finished, yet.
        game_results = nfl_game.evaluate_game()
        assert len(game_results) == 3
        assert game_results[p1] == 0
        assert game_results[p2] == 0
        assert game_results[p3] == 0

        nfl_game.final = True
        game_results = nfl_game.evaluate_game()
        assert game_results[p1] == 0
        assert game_results[p2] == 1
        assert game_results[p3] == 0

    def test_is_monday_night(self, nfl_game):
        assert not nfl_game.is_monday_night()

        nfl_game.timestamp = nfl_game.timestamp.replace(day=12)
        assert nfl_game.is_monday_night()


@pytest.mark.django_db
class TestTeamModel:
    def test_full_name(self):
        cur_team = Team.objects.get(id=TeamChoices.CHI)
        assert cur_team.full_name == TeamChoices.CHI.label
        cur_team = Team.objects.get(id=TeamChoices.TB)
        assert cur_team.full_name == TeamChoices.TB.label

    def test_short_name(self):
        cur_team = Team.objects.get(id=TeamChoices.CHI)
        assert cur_team.short_name == "Bears"
        cur_team = Team.objects.get(id=TeamChoices.TB)
        assert cur_team.short_name == "Buccaneers"

    def test_string(self):
        cur_team = Team.objects.get(id=TeamChoices.CHI)
        assert str(cur_team) == "Chicago Bears"


@pytest.mark.django_db
class TestPickModel:
    def test_string(self, pick):
        assert str(pick) == (
            f"{pick.user.first_name} picked 'Home Team' for Buffalo Bills"
            " at Atlanta Falcons on 2019-08-08 23:00:00+00:00"
        )

    def test_awarded_points(self, pick):
        pick.game.final = True
        pick.game.home_team_score = 23
        pick.game.visitor_team_score = 27
        assert pick.awarded_points == 0

        pick.game.home_team_score = 28
        assert pick.awarded_points == 1

    def test_tie_break(self, pick):
        pick.game.final = True
        pick.game.home_team_score = 23
        pick.game.visitor_team_score = 27

        assert pick.tie_break == 50

        pick.selection = PickChoices.VISITOR_TEAM
        assert pick.tie_break == 19

        pick.picked_tie_break = 4
        assert pick.tie_break == 0


@pytest.mark.django_db
class TestWeekModel:
    def test_evaluate_week(self, nfl_games, make_pick, make_pick_pool_user):
        user1 = make_pick_pool_user()
        user2 = make_pick_pool_user()
        user3 = make_pick_pool_user()
        user4 = make_pick_pool_user()
        for idx, game in enumerate(Game.objects.all()):
            make_pick(user=user1, game=game)
            make_pick(
                user=user2,
                game=game,
                selection=PickChoices.VISITOR_TEAM,
            )
            make_pick(user=user3, game=game)
            if idx % 2 == 0:
                make_pick(user=user4, game=game, selection=PickChoices.VISITOR_TEAM)
            else:
                make_pick(user=user4, game=game)
            game.final = True
            game.home_team_score = 3
            game.visitor_team_score = 7
            game.save()
        res = Week.objects.evaluate_week(2019, 5)
        assert len(res) == 3
        assert res[0] == (17, [user2])
        assert res[1] == (9, [user4])
        assert res[2] == (0, [user1, user3])
