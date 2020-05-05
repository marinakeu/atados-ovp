from mock import Mock

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser

from ovp.apps.users.models import User

from ovp.apps.projects.models.project import Project

from ovp.apps.channels.models import Channel
from ovp.apps.channels.tests.helpers.views import ChannelProjectTestViewSet
from ovp.apps.channels.tests.helpers.views import OverrideQuerysetTestViewSet
from ovp.apps.channels.middlewares.channel import ChannelRecognizerMiddleware


class ChannelViewsetDecoratorTestCase(TestCase):
    """
    Test channel decorator restricts querysets per channel.

    We test the decorator through the viewset.
    """

    def setUp(self):
        # Set up channels
        channel1 = Channel(name="Channel One", slug="channel1")
        channel1.save()

        # Set up test projects
        user = User.objects.create(
            email="test@default.com",
            password="abc",
            object_channel="default"
        )

        project1 = Project.objects.create(
            name="test1",
            owner=user,
            object_channel="default"
        )
        project2 = Project.objects.create(
            name="test2",
            owner=user,
            object_channel="channel1"
        )
        project3 = Project.objects.create(
            name="test3",
            owner=user,
            object_channel="channel1"
        )

        # Set up test view
        self.factory = RequestFactory()

    def _generate_request(self):
        request = self.factory.get("/test/")
        request.user = AnonymousUser()
        request.session = {}
        return request

    def test_channels_restriction_through_get_queryset(self):
        # We also pass it through the middleware
        cm = ChannelRecognizerMiddleware(
            ChannelProjectTestViewSet.as_view({'get': 'list'})
        )
        request = self._generate_request()
        response = cm(request)
        self.assertEqual(response.data["count"], 1)

        request = self._generate_request()
        request.META["HTTP_X_OVP_CHANNEL"] = "channel1"
        response = cm(request)
        self.assertEqual(response.data["count"], 2)

    def test_channels_restriction_through_queryset_property(self):
        """
        Assert it's not possible to use self.queryset
        directly on decorated views
        """
        cm = ChannelRecognizerMiddleware(
            OverrideQuerysetTestViewSet.as_view({'get': 'list'})
        )
        request = self._generate_request()
        response = cm(request)
        self.assertEqual(response.data["count"], 1)

        request = self._generate_request()
        request.META["HTTP_X_OVP_CHANNEL"] = "channel1"
        response = cm(request)
        self.assertEqual(response.data["count"], 2)
