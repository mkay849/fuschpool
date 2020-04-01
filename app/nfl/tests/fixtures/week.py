import pytest

from nfl.models import Week, Year


@pytest.fixture
def year(db):
    """Fixture creating a year."""
    return Year.objects.get_or_create(year=2019)[0]


@pytest.fixture
def week(make_week):
    """Fixture creating a week."""
    return make_week()


@pytest.fixture
def make_week(year):
    """Fixture factory to create a nfl week."""
    def _make_week(**kwargs):
        return Week.objects.get_or_create(
            week=kwargs.get("week", 2),
            year=kwargs.get("year", year)
        )[0]
    return _make_week
