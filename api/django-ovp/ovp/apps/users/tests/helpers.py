from ovp.apps.users.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from oauth2_provider.models import Application


def create_user(
        email="validemail@gmail.com",
        password="validpassword",
        extra_data={},
        headers={}):
    data = {
        'name': 'Valid Name',
        'email': email,
        'password': password
    }
    data = dict(data, **extra_data)

    client = APIClient()
    return client.post(reverse('user-list'), data, format="json", **headers)


def create_user_with_profile(
        email="validemail@gmail.com",
        password="validpassword",
        profile={},
        headers={}):
    data = {
        'name': 'Valid Name',
        'email': email,
        'password': password,
        'profile': profile
    }

    client = APIClient()
    return client.post(reverse('user-list'), data, format="json", **headers)


def authenticate(
        email='test_can_login@test.com',
        password='validpassword',
        headers={}):
    a = Application.objects.create(
        authorization_grant_type="password",
        client_type="confidential")
    client_id = a.client_id
    client_secret = a.client_secret

    data = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': email,
        'password': password
    }

    client = APIClient()
    return client.post(reverse('token'), data, format="json", **headers)


def create_token(email='test@recovery.token', headers={}):
    data = {
        'email': email,
    }

    client = APIClient()
    return client.post(reverse('recovery-token-list'),
                       data, format="json", **headers)


def create_email_token(email='test@email.token', headers={}):
    user = User.objects.get(email=email)
    client = APIClient()
    client.force_authenticate(user)

    return client.post(
        reverse('request-email-verification-list'),
        format="json",
        **headers)
