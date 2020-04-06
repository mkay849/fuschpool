from datetime import date
import pytest

from core.models import PickPoolUser

user_instance = 0


@pytest.fixture
def pick_pool_user(make_pick_pool_user):
    return make_pick_pool_user()


@pytest.fixture
def make_pick_pool_user(db):
    def _make_pick_pool_user(instance: int = 1, **kwargs):
        global user_instance

        user_instance += 1
        return PickPoolUser.objects.get_or_create(
            username=kwargs.get("username", f"user{user_instance}"),
            password=kwargs.get("password", f"{user_instance}password"),
            first_name=kwargs.get("first_name", f"First name {user_instance}"),
            last_name=kwargs.get("last_name", f"Last name {user_instance}"),
            email=kwargs.get("email", f"email{user_instance}@localhost.lan"),
            birth_date=kwargs.get("birth_date", date(1984, 1, 1)),
        )[0]

    return _make_pick_pool_user
