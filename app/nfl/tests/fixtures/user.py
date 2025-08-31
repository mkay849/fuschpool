import pytest


@pytest.fixture
def user(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="testuser", password="password"
    )
    yield user
    user.delete()
