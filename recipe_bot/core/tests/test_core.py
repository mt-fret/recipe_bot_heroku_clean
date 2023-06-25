import pytest
from django.contrib.auth.models import User
from django.contrib import auth


# test user created and logged in
@pytest.mark.django_db
def test_signup(client):
    data = {
        'username': 'test_user',
        'password1': 'test_password',
        'password2': 'test_password'
    }
    r = client.post('/signup/', data)

    user = auth.get_user(client)
    assert r.status_code == 302
    assert len(User.objects.all()) == 1
    assert user == User.objects.all().first()


# test user can't create user with existing username
@pytest.mark.django_db
def test_signup_same_username(client, created_user):
    data = {
        'username': 'test_user',
        'password1': 'test_password',
        'password2': 'test_password'
    }
    r = client.post('/signup/', data)

    assert r.status_code == 200
    assert len(User.objects.all()) == 1

