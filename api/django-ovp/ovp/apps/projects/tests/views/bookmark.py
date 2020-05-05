from django.test import TestCase

from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.users.models import User

from ovp.apps.projects.models import ProjectBookmark
from ovp.apps.projects.models import Project

from ovp.apps.channels.models import ChannelSetting


class ProjectBookmarkTestCase(TestCase):

    def setUp(self):
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

        self.user = User.objects.create(
            email="sample@user.com",
            password="sample@user.com",
            object_channel="default"
        )
        self.project = Project.objects.create(
            name="test project",
            description="test project",
            owner=self.user,
            object_channel="default"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_can_bookmark(self):
        """ Assert it's possible to bookmark a project"""
        self.assertEqual(ProjectBookmark.objects.count(), 0)

        response = self.client.post(
            reverse("project-bookmark", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["detail"],
            "Object sucesfully bookmarked."
        )
        self.assertEqual(response.data["success"], True)
        self.assertEqual(ProjectBookmark.objects.count(), 1)

        self.assertEqual(ProjectBookmark.objects.first().user, self.user)
        self.assertEqual(ProjectBookmark.objects.first().project, self.project)

    def test_cant_bookmark_twice(self):
        """ Assert it's not possible to bookmark a project twice """
        self.test_can_bookmark()

        self.assertEqual(ProjectBookmark.objects.count(), 1)
        response = self.client.post(
            reverse("project-bookmark", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Can't bookmark an object that has been already bookmarked."
        )
        self.assertEqual(response.data["success"], False)
        self.assertEqual(ProjectBookmark.objects.count(), 1)

    def test_can_unbookmark(self):
        """ Assert it's possible to unbookmark a project """
        self.test_can_bookmark()
        self.assertEqual(ProjectBookmark.objects.count(), 1)
        response = self.client.post(
            reverse("project-unbookmark", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["detail"],
            "Object sucesfully unbookmarked."
        )
        self.assertEqual(response.data["success"], True)
        self.assertEqual(ProjectBookmark.objects.count(), 0)

    def test_cant_unbookmark_unbookmarked(self):
        """
        Assert it's possible to unbookmark a project that is not bookmarked
        """
        self.assertEqual(ProjectBookmark.objects.count(), 0)
        response = self.client.post(
            reverse("project-unbookmark", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Can't unbookmark an object that it not bookmarked."
        )
        self.assertEqual(response.data["success"], False)
        self.assertEqual(ProjectBookmark.objects.count(), 0)

    def test_can_retrive_bookmarked(self):
        """ Assert it's possible to retrieve bookmarked projects """
        response = self.client.get(
            reverse("project-bookmarked"),
            format="json"
        )
        self.assertEqual(response.data["count"], 0)

        self.test_can_bookmark()
        response = self.client.get(
            reverse("project-bookmarked"),
            format="json"
        )
        self.assertEqual(response.data["count"], 1)

    def test_cant_access_bookmark_routes_logged_out(self):
        """
        Assert it's not possible to access bookmark routes if unauthenticated
        """
        client = APIClient()

        response = client.post(
            reverse("project-bookmark", ["test-project"]),
            format="json"
        )
        self.assertTrue(response.status_code == 401)

        response = client.post(
            reverse("project-unbookmark", ["test-project"]),
            format="json"
        )
        self.assertTrue(response.status_code == 401)

        response = client.get(reverse("project-bookmarked"), format="json")
        self.assertTrue(response.status_code == 401)

    def test_project_include_is_bookmarked_info(self):
        """
        Assert project includes information if it's bookmarked or not
        """
        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data["is_bookmarked"], False)

        self.test_can_bookmark()

        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data["is_bookmarked"], True)

    def test_project_include_bookmarked_count(self):
        """
        Assert project includes information about bookmark count
        """
        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data["bookmark_count"], 0)

        self.test_can_bookmark()

        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data["bookmark_count"], 1)

    def test_project_hides_bookmarked_count_if_set(self):
        """
        Assert project hides information about
        bookmark count if setting disabled
        """
        ChannelSetting.objects.create(
            key="ENABLE_PROJECT_BOOKMARK_COUNT",
            value="0",
            object_channel="default"
        )
        cache.clear()

        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data["bookmark_count"], None)

        self.test_can_bookmark()

        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data["bookmark_count"], None)
