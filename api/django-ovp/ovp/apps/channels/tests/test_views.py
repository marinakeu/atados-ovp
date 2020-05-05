from django.test import TestCase
from django.test.client import RequestFactory
from django.urls.exceptions import NoReverseMatch

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.channels.models import Channel

from ovp.apps.projects.models import Project

from ovp.apps.organizations.models import Organization

from ovp.apps.users.models import User

from oauth2_provider.models import Application


class ChannelCreateViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        Channel(name="Test", slug="test-channel").save()

        # Attempt to test with a test route
        # If the test sandbox does not include an test url(as
        # in when testing with actual production settings), then
        # use an actual route that is known to implement channels
        try:
            self.test_route = reverse("test-users-list")
        except NoReverseMatch:
            self.test_route = reverse("user-list")

    def test_requests_create_objects_on_default_channel(self):
        """
        Assert object defaults to default channel
        if no header is supplied
        """
        data = {
            "name": "Valid Name",
            "email": "test@email.com",
            "password": "123456789abcdefg"
        }
        response = self.client.post(
            self.test_route,
            data,
            format="json"
        )

        user = User.objects.first()
        self.assertTrue(user.channel.slug == "default")

    def test_requests_create_objects_on_correct_channel(self):
        """
        Assert object are created on the correct channel
        if header is supplied
        """
        data = {
            "name": "Valid Name",
            "email": "test@email.com",
            "password": "123456789abcdefg"
        }
        response = self.client.post(
            self.test_route,
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )

        user = User.objects.first()
        self.assertTrue(user.channel.slug == "test-channel")


class ChannelPermissionsTestCase(TestCase):
    """
    This TestCase asserts an user can't access
    resources with an authentication from another channel
    """

    def setUp(self):
        self.user = User.objects.create(
            email="sample_user@gmail.com",
            password="sample_user",
            object_channel="default"
        )
        self.organization = Organization.objects.create(
            name="sample organization",
            owner=self.user,
            object_channel="default"
        )
        self.data = {
            "name": "Valid Name",
            "details": "test details",
            "address": {
                "typed_address": "r. tecainda, 81, sao paulo"
            },
            "disponibility": {
                "type": "work",
                "work": {
                    "description": "abc"
                }
            },
            "owner": self.user.pk,
            "organization_id": self.organization.pk
        }

        self.client = APIClient()
        Channel(name="Test", slug="test-channel").save()

        # Attempt to test with a test route
        # If the test sandbox does not include an test url(as
        # in when testing with actual production settings), then
        # use an actual route that is known to implement channels
        try:
            self.test_route = reverse("test-projects-list")
        except NoReverseMatch:
            self.test_route = reverse("project-list")

    def test_accessing_another_channel_resource(self):
        """
        Assert it's impossible to access another
        channel resource while authenticated
        """
        a = Application.objects.create(
            authorization_grant_type="password",
            client_type="confidential"
        )
        client_id = a.client_id
        client_secret = a.client_secret

        # Wrong request with jwt token
        token = self.client.post(
            reverse("token"),
            {
                "username": "sample_user@gmail.com",
                "password": "sample_user",
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret
            },
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        ).data["access_token"]
        response = self.client.post(
            self.test_route,
            self.data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b'{"detail": "Invalid channel for user token."}'
        )

        # Wrong request with client login
        self.client.login(
            email="sample_user@gmail.com",
            password="sample_user",
            channel="default"
        )
        response = self.client.post(
            self.test_route,
            self.data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b'{"detail": "Invalid channel for user token."}'
        )

        # Correct request
        response = self.client.post(
            self.test_route,
            self.data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 201)
