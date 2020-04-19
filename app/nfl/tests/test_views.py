import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestPicksView:
    def test_view_url_exists_at_desired_location(self, client):
        response = client.get("/nfl/picks/")
        assert response.status_code == 200

    def test_view_url_accessible_by_name(self, client):
        response = client.get(reverse("make_picks"))
        assert response.status_code == 200

    def test_view_uses_correct_template(self, client):
        response = client.get(reverse("make_picks"))
        assert response.status_code == 200
        assert "nfl/picks.html" in (t.name for t in response.templates)
