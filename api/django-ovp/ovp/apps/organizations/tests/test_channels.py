import copy

from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from ovp.apps.organizations.models import Organization
from ovp.apps.channels.models import Channel
from ovp.apps.users.models import User

base_organization = {
    "name": "test organization",
    "slug": "test-override-slug",
    "description": "test description",
    "details": "test details",
    "type": 0,
    "address": {
        "typed_address": "r. tecainda, 81, sao paulo"
    },
    "causes": [
        {"id": 1},
        {"id": 2}
    ],
    "contact_name": "test contact name",
    "contact_phone": "+551112345678",
    "contact_email": "test@contact.com"
}


class OrganizationChannelTestCase(TestCase):
    def setUp(self):
        self.channel = Channel.objects.create(
            name="Test channel", slug="test-channel")
        self.user1 = User.objects.create_user(
            email="test@email.com",
            password="testpwpw",
            object_channel="default")
        self.user2 = User.objects.create_user(
            email="test@email.com",
            password="testpwpw",
            object_channel="test-channel")

    def test_organizations_are_created_on_correct_channel(self):
        """ Assert organizations are created on the correct channel """
        data = copy.copy(base_organization)

        client = APIClient()
        client.login(
            email="test@email.com",
            password="testpwpw",
            channel="test-channel")

        response = client.post(
            reverse("organization-list"),
            data,
            format="json")
        self.assertTrue(response.status_code == 400)

        response = client.post(
            reverse("organization-list"),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel")
        self.assertTrue(response.status_code == 201)

        organization = Organization.objects.get(pk=response.data["id"])
        self.assertTrue(organization.channel.slug == "test-channel")

    def test_cant_modify_organizations_on_another_channel(self):
        """
        Make sure users from an organization can't modify
        the same organization on another channel
        """
        self.test_organizations_are_created_on_correct_channel()

        client = APIClient()

        client.login(
            email="test@email.com",
            password="testpwpw",
            channel="default")
        response = client.patch(reverse("organization-detail",
                                        ["test-organization"]),
                                {"description": "another description"},
                                format="json",
                                HTTP_X_OVP_CHANNEL="test-channel")
        self.assertTrue(response.status_code == 400)

        client.login(
            email="test@email.com",
            password="testpwpw",
            channel="default")
        response = client.patch(reverse("organization-detail",
                                        ["test-organization"]),
                                {"description": "another description"},
                                format="json",
                                HTTP_X_OVP_CHANNEL="default")
        self.assertTrue(response.status_code == 404)

        client.login(
            email="test@email.com",
            password="testpwpw",
            channel="test-channel")
        response = client.patch(reverse("organization-detail",
                                        ["test-organization"]),
                                {"description": "another description"},
                                format="json",
                                HTTP_X_OVP_CHANNEL="test-channel")
        self.assertTrue(response.status_code == 200)
