from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.users.models import User
from ovp.apps.users.models import PasswordRecoveryToken
from ovp.apps.users.models import PasswordHistory
from ovp.apps.users.tests.helpers import create_user
from ovp.apps.users.tests.helpers import create_token

from ovp.apps.channels.models import Channel

from oauth2_provider.models import Application


class UserChannelTestCase(TestCase):
    def setUp(self):
        Channel.objects.create(name="Test channel", slug="test-channel")
        Channel.objects.create(name="Wrong channel", slug="wrong-channel")
        self.client = APIClient()

        self.user1 = User.objects.create(
            email="sample_user@gmail.com",
            password="sample_user",
            object_channel="default")
        self.user2 = User.objects.create(
            email="sample_user@gmail.com",
            password="sample_user",
            object_channel="test-channel")

    def test_users_with_same_email_on_different_channel(self):
        """
        Test users can be created with the same email but on different channel
        """
        self.assertEqual(User.objects.count(), 2)

        with self.assertRaises(IntegrityError) as raised:
            user3 = User.objects.create(
                email="sample_user@gmail.com",
                password="sample_user",
                object_channel="default")
        self.assertEqual(IntegrityError, type(raised.exception))

    def test_user_channel_based_auth_backend(self):
        """ Test user authentication on different channel """
        user1 = authenticate(
            email="sample_user@gmail.com",
            password="sample_user",
            channel="default")
        user2 = authenticate(
            email="sample_user@gmail.com",
            password="sample_user",
            channel="test-channel")

        self.assertEqual(user1, self.user1)
        self.assertEqual(user2, self.user2)
        self.assertTrue(user1 is not None)
        self.assertTrue(user2 is not None)

    def test_user_channel_based_auth_view(self):
        """ Test user authentication on different channel """
        a = Application.objects.create(
            authorization_grant_type="password",
            client_type="confidential")
        client_id = a.client_id
        client_secret = a.client_secret

        # Authenticate user one
        response = self.client.post(reverse("token"),
                                    {"username": "sample_user@gmail.com",
                                     "password": "sample_user",
                                     "grant_type": "password",
                                     "client_id": client_id,
                                     "client_secret": client_secret},
                                    format="json",
                                    HTTP_X_OVP_CHANNEL="default")
        self.assertTrue(response.status_code == 200)
        self.assertTrue("access_token" in response.data)

        # Authenticate user two
        response = self.client.post(reverse("token"),
                                    {"username": "sample_user@gmail.com",
                                     "password": "sample_user",
                                     "grant_type": "password",
                                     "client_id": client_id,
                                     "client_secret": client_secret},
                                    format="json",
                                    HTTP_X_OVP_CHANNEL="test-channel")
        self.assertTrue(response.status_code == 200)
        self.assertTrue("access_token" in response.data)

        # Wrong channel authentication
        response = self.client.post(reverse("token"),
                                    {"username": "sample_user@gmail.com",
                                     "password": "sample_user",
                                     "grant_type": "password",
                                     "client_id": client_id,
                                     "client_secret": client_secret},
                                    format="json",
                                    HTTP_X_OVP_CHANNEL="wrong-channel")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(
            response.data == {
                "error": "invalid_grant",
                "error_description": "Invalid credentials given."})

    def test_channel_based_user_creation(self):
        """ Test user channel based user creation """
        create_user()
        self.assertEqual(User.objects.last().channel.slug, "default")

        create_user(headers={"HTTP_X_OVP_CHANNEL": "test-channel"})
        self.assertEqual(User.objects.last().channel.slug, "test-channel")

        response = create_user(headers={"HTTP_X_OVP_CHANNEL": "test-channel"})
        self.assertEqual(
            response.data, {
                "email": ["An user with this email is already registered."]})

    def test_channel_based_user_retrieval(self):
        """ Test user channel based user retrieval """
        self.test_channel_based_user_creation()
        self.client.force_authenticate(
            User.objects.get(
                email="validemail@gmail.com",
                channel__slug="default"))
        response = self.client.get(
            reverse("user-current-user"), {}, format="json")
        uuid1 = response.data["uuid"]

        self.client.force_authenticate(
            User.objects.get(
                email="validemail@gmail.com",
                channel__slug="test-channel"))
        response = self.client.get(
            reverse("user-current-user"),
            {},
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel")
        uuid2 = response.data["uuid"]

        self.assertTrue(uuid1 != uuid2)

    def test_channel_based_password_recovery(self):
        """ Test user creation and retrieving """
        self.test_channel_based_user_creation()

        # Create token
        response = create_token(
            email="validemail@gmail.com", headers={
                "HTTP_X_OVP_CHANNEL": "test-channel"})
        self.assertEqual(
            PasswordRecoveryToken.objects.last().channel.slug,
            "test-channel")

        # Recover password
        data = {
            "email": "validemail@gmail.com",
            "token": PasswordRecoveryToken.objects.last().token,
            "new_password": "newpwvalidpw*"}

        # Attempt to use token from another channel
        response = self.client.post(
            reverse("recover-password-list"), data, format="json")
        self.assertTrue(response.data["message"] == "Invalid token.")

        # Use token
        response = self.client.post(
            reverse("recover-password-list"),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel")
        self.assertTrue(response.data["message"] == "Password updated.")
        self.assertTrue(
            PasswordHistory.objects.last().channel.slug == "test-channel")
