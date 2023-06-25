import pytest
from django.contrib.auth.models import User


@pytest.fixture
def created_user():
    user = User.objects.create_user(
        username='test_user',
        password='test_password'
    )

    return user