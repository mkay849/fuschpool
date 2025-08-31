from datetime import UTC, datetime, timedelta

import pytest
from nfl.models import Week, Year


@pytest.fixture
def year(db):
    """Fixture creating a year."""
    return Year.objects.get_or_create(
        start_timestamp=datetime(2019, 7, 17, 7, tzinfo=UTC),
        end_timestamp=datetime(2020, 2, 16, 7, 59, tzinfo=UTC),
        value=2019,
    )[0]


@pytest.fixture
def week(make_week):
    """Fixture creating a week."""
    return make_week()


@pytest.fixture
def make_week(year):
    """Fixture factory to create a nfl week."""

    def _make_week(**kwargs):
        cur_year = kwargs.get("year", year)
        week = kwargs.get("week", 5)
        start_timestamp = cur_year.start_timestamp + timedelta(weeks=week)
        end_timestamp = start_timestamp + timedelta(weeks=1) - timedelta(minutes=1)
        return Week.objects.get_or_create(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            value=week,
            year=cur_year,
        )[0]

    return _make_week
