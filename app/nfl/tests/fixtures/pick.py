import pytest

from nfl.defines import PickChoices
from nfl.models import Pick


@pytest.fixture
def pick(make_pick):
    return make_pick()


@pytest.fixture
def make_pick(nfl_game, pick_pool_user):
    def _make_pick(**kwargs):
        return Pick.objects.get_or_create(
            user=kwargs.get("user", pick_pool_user),
            game=kwargs.get("game", nfl_game),
            selection=kwargs.get("selection", PickChoices.HOME_TEAM),
            picked_tie_break=kwargs.get("tie_break", 23),
        )[0]

    return _make_pick
