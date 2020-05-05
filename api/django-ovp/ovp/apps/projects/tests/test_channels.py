from django.test import TestCase
from django.core.cache import cache

from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from ovp.apps.projects.models import Project
from ovp.apps.projects.models import Work
from ovp.apps.projects.models import Job
from ovp.apps.projects.models import JobDate
from ovp.apps.projects.models import Apply
from ovp.apps.users.models import User
from ovp.apps.organizations.models import Organization
from ovp.apps.channels.models import Channel
from ovp.apps.channels.models.channel_setting import ChannelSetting


import copy

base_project = {
    "name": "test project",
    "slug": "test-cant-override-slug-on-creation",
    "details": "this is just a test project",
    "description": "the project is being tested",
    "minimum_age": 18,
    "address": {
        "typed_address": "r. tecainda, 81, sao paulo"
    },
    "disponibility": {
        "type": "work",
        "work": {
            "description": "abc"
        }
    },
    "causes": [{"id": 1}, {"id": 2}],
    "skills": [{"id": 3}, {"id": 4}]
}


class ProjectChannelTestCase(TestCase):

    def setUp(self):
        # Channel
        channel = Channel.objects.create(
            name="Test channel",
            slug="test-channel"
        )

        # Settings
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="test-channel"
        )
        cache.clear()

        # Users
        self.email = "test_can_create_project@gmail.com"
        self.password = "testcancreate"
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            object_channel="default"
        )
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            object_channel="test-channel"
        )

    def test_creating_project_creates_objects_on_correct_channel(self):
        """
        Assert creating a project creates the object on the correct channel
        """
        client = APIClient()
        client.login(
            email=self.email,
            password=self.password,
            channel="test-channel"
        )

        # Create
        data = copy.copy(base_project)
        response = client.post(
            reverse("project-list"),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )
        self.assertTrue(response.status_code == 201)
        self.assertTrue(Project.objects.last().channel.slug == "test-channel")
        self.assertTrue(Work.objects.last().channel.slug == "test-channel")

        # Modify
        updated_project = {
            "disponibility": {
                "type": "job",
                "job": {
                    "dates": [
                        {
                            "name": "update",
                            "start_date": "2013-01-29T12:34:56.123Z",
                            "end_date": "2013-01-29T13:34:56.123Z"
                        },
                        {
                            "name": "test1",
                            "start_date": "2013-02-01T12:34:56.123Z",
                            "end_date": "2013-02-01T13:34:56.123Z"
                        }
                    ]
                }
            }
        }
        response = client.patch(
            reverse("project-detail", ["test-project"]),
            updated_project,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )
        self.assertTrue(Job.objects.last().channel.slug == "test-channel")
        self.assertTrue(JobDate.objects.last().channel.slug == "test-channel")

    def test_cant_create_modify_on_another_channel(self):
        """
        Assert it's not possible to create or modify object on another channel
        """
        client = APIClient()
        client.login(
            email=self.email,
            password=self.password,
            channel="test-channel"
        )

        # Create
        data = copy.copy(base_project)
        response = client.post(
            reverse("project-list"),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertTrue(response.status_code == 400)

        response = client.post(
            reverse("project-list"),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )
        self.assertTrue(response.status_code == 201)

        # Modify
        updated_project = {
            "disponibility": {
                "type": "job",
                "job": {
                    "dates": [
                        {
                            "name": "update",
                            "start_date": "2013-01-29T12:34:56.123Z",
                            "end_date": "2013-01-29T13:34:56.123Z"
                        },
                        {
                            "name": "test1",
                            "start_date": "2013-02-01T12:34:56.123Z",
                            "end_date": "2013-02-01T13:34:56.123Z"
                        }
                    ]
                }
            }
        }
        response = client.patch(
            reverse("project-detail", ["test-project"]),
            updated_project,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertTrue(response.status_code == 400)

    def test_applies_are_saved_on_correct_channel(self):
        """
        Assert apply objects are saved on correct channel
        """
        self.test_creating_project_creates_objects_on_correct_channel()
        client = APIClient()
        client.login(
            email=self.email,
            password=self.password,
            channel="test-channel"
        )

        response = client.post(
            reverse("project-applies-apply", ["test-project"]),
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(Apply.objects.last().channel.slug == "test-channel")

    def test_cant_apply__from_another_channel(self):
        """
        Assert it's not possible to apply from another channel
        """
        self.test_creating_project_creates_objects_on_correct_channel()
        client = APIClient()
        client.login(
            email=self.email,
            password=self.password,
            channel="test-channel"
        )

        response = client.post(
            reverse("project-applies-apply", ["test-project"]),
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertTrue(response.status_code == 400)
