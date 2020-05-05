import re

from django.test import TestCase
from django.core import mail
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.users.tests.helpers import authenticate
from ovp.apps.users.tests.helpers import create_user
from ovp.apps.users.tests.helpers import create_email_token
from ovp.apps.users.models import User

from ovp.apps.channels.models.channel_setting import ChannelSetting


class RequestEmailVerificationViewSetTestCase(TestCase):
    def test_can_create_token(self):
        """Assert that it's possible to create an email token"""
        user = create_user('test@email.token')
        response = create_email_token('test@email.token')
        self.assertTrue(response.data['success'])

    def test_cant_create_6_tokens(self):
        """Assert that it's impossible to create more than 5 tokens in less than 60 minutes"""
        user = create_user('test2@email.token')
        response = None
        for i in range(6):
            response = create_email_token('test2@email.token')

        self.assertFalse(response.data.get('success', False))


class VerificateEmailViewSetTestCase(TestCase):
    def test_can_verify_email(self):
        """Assert the user can verify his email"""
        # request token
        user = create_user('test_can_validate@email.com')

        mail.outbox = []  # clear outbox
        response = create_email_token('test_can_validate@email.com')
        self.assertEqual(User.objects.last().is_email_verified, False)

        # get token from mailbox
        email_content = mail.outbox[0].alternatives[0][0]
        token = re.search(
            '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            email_content).group(0)

        # verificate email
        data = {
            'token': token,
        }

        client = APIClient()
        response = client.post(
            reverse('email-verification-list'),
            data,
            format="json")
        self.assertEqual(response.data['message'], 'Email is now verified.')
        self.assertEqual(User.objects.last().is_email_verified, True)

    def test_cant_verify_invalid_token(self):
        """Assert that it's impossible to verify email with invalid token"""
        # Request token
        user = create_user('test_cant_verify@email.com')
        response = create_email_token('test_cant_verify@email.com')

        # Verify email
        data = {
            'token': 'invalid_token',
        }

        client = APIClient()
        response = client.post(
            reverse('email-verification-list'),
            data,
            format="json")
        self.assertEqual(response.data['message'], 'Invalid token.')
        self.assertEqual(response.status_code, 401)
