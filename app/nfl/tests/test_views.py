from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestPicksView:
    def test_view_url_exists_at_desired_location(self, client, user):
        response = client.get("/nfl/picks/")
        assert response.status_code == HTTPStatus.FOUND
        client.force_login(user)
        response = client.get("/nfl/picks/")
        assert response.status_code == HTTPStatus.OK

    def test_view_url_accessible_by_name(self, client, user):
        response = client.get(reverse("nfl:picks"))
        assert response.status_code == HTTPStatus.FOUND
        client.force_login(user)
        response = client.get(reverse("nfl:picks"))
        assert response.status_code == HTTPStatus.OK

    def test_view_uses_correct_template(self, client, user):
        response = client.get(reverse("nfl:picks"))
        assert response.status_code == HTTPStatus.FOUND
        client.force_login(user)
        response = client.get(reverse("nfl:picks"))
        assert response.status_code == HTTPStatus.OK
        assert "nfl/picks.html" in (t.name for t in response.templates)
