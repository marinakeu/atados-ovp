from django.test import TestCase

from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.users.models import User

from ovp.apps.organizations.models import OrganizationBookmark
from ovp.apps.organizations.models import Organization

from ovp.apps.channels.models import ChannelSetting


class OrganizationBookmarkTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="sample@user.com",
            password="sample@user.com",
            object_channel="default")

        self.organization = Organization.objects.create(
            name="test organization",
            description="test organization",
            owner=self.user,
            object_channel="default")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_can_bookmark(self):
        """ Assert it's possible to bookmark a organization """
        self.assertEqual(OrganizationBookmark.objects.count(), 0)

        response = self.client.post(
            reverse(
                "organization-bookmark",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["detail"],
            "Object sucesfully bookmarked.")
        self.assertEqual(response.data["success"], True)
        self.assertEqual(OrganizationBookmark.objects.count(), 1)

        self.assertEqual(OrganizationBookmark.objects.first().user, self.user)
        self.assertEqual(
            OrganizationBookmark.objects.first().organization,
            self.organization)

    def test_cant_bookmark_twice(self):
        """ Assert it's not possible to bookmark a organization twice """
        self.test_can_bookmark()

        self.assertEqual(OrganizationBookmark.objects.count(), 1)
        response = self.client.post(
            reverse(
                "organization-bookmark",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Can't bookmark an object that has been already bookmarked.")
        self.assertEqual(response.data["success"], False)
        self.assertEqual(OrganizationBookmark.objects.count(), 1)

    def test_can_unbookmark(self):
        """ Assert it's possible to unbookmark a organization """
        self.test_can_bookmark()
        self.assertEqual(OrganizationBookmark.objects.count(), 1)
        response = self.client.post(
            reverse(
                "organization-unbookmark",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["detail"],
            "Object sucesfully unbookmarked.")
        self.assertEqual(response.data["success"], True)
        self.assertEqual(OrganizationBookmark.objects.count(), 0)

    def test_cant_unbookmark_unbookmarked(self):
        """
        Assert it's possible to unbookmark a organization
        that is not bookmarked
        """
        self.assertEqual(OrganizationBookmark.objects.count(), 0)
        response = self.client.post(
            reverse(
                "organization-unbookmark",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Can't unbookmark an object that it not bookmarked.")
        self.assertEqual(response.data["success"], False)
        self.assertEqual(OrganizationBookmark.objects.count(), 0)

    def test_can_retrive_bookmarked(self):
        """ Assert it's possible to retrieve bookmarked organizations """
        response = self.client.get(
            reverse("organization-bookmarked"),
            format="json")
        self.assertEqual(response.data["count"], 0)

        self.test_can_bookmark()
        response = self.client.get(
            reverse("organization-bookmarked"),
            format="json")
        self.assertEqual(response.data["count"], 1)

    def test_cant_access_bookmark_routes_logged_out(self):
        """
        Assert it's not possible to access bookmark routes if unauthenticated
        """
        client = APIClient()

        response = client.post(
            reverse(
                "organization-bookmark",
                ["test-organization"]),
            format="json")
        self.assertTrue(response.status_code == 401)

        response = client.post(
            reverse(
                "organization-unbookmark",
                ["test-organization"]),
            format="json")
        self.assertTrue(response.status_code == 401)

        response = client.get(
            reverse("organization-bookmarked"),
            format="json")
        self.assertTrue(response.status_code == 401)

    def test_organization_include_is_bookmarked_info(self):
        """
        Assert organization includes information if it's bookmarked or not
        """
        response = self.client.get(
            reverse(
                "organization-detail",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.data["is_bookmarked"], False)

        self.test_can_bookmark()

        response = self.client.get(
            reverse(
                "organization-detail",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.data["is_bookmarked"], True)
