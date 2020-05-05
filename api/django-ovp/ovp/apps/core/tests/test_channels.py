from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.channels.models import Channel

from ovp.apps.core.models import Skill
from ovp.apps.core.models import Lead
from ovp.apps.core.models import ChannelContact
from ovp.apps.core.models import GoogleAddress


class ChannelsTestCase(TestCase):

    def setUp(self):
        TestChannel = Channel.objects.create(
            name="Test Channel",
            slug="test-channel"
        )
        Skill.objects.filter(channel=TestChannel).delete()
        Skill.objects.create(name="test1", object_channel="test-channel")
        Skill.objects.create(name="test2", object_channel="test-channel")

    def test_startup_route(self):
        """
        Assert startup route returns results based by channel
        """
        client = APIClient()
        response = client.get(
            reverse("startup"),
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(len(response.data["skills"]), 12)
        self.assertEqual(len(response.data["causes"]), 13)

        response = client.get(
            reverse("startup"),
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )
        self.assertEqual(len(response.data["skills"]), 2)
        self.assertEqual(len(response.data["causes"]), 13)

    def test_contact_route(self):
        """
        Assert contact route cross checks contacts of the channel
        """
        data = {
            "name": "my-name",
            "message": "my message",
            "email": "reply_to@asddsa.com",
            "phone": "+5511912345678",
            "recipients": ["test-channel-contact@1.com"]
        }
        ChannelContact.objects.create(
            email="test-channel-contact@1.com",
            object_channel="test-channel"
        )

        response = self.client.post(
            reverse("contact"),
            data=data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertTrue(response.status_code == 400)

        response = self.client.post(
            reverse("contact"),
            data=data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )
        self.assertTrue(response.status_code == 200)

    def test_leads_route(self):
        """
        Assert leads route creates objects in the correct channel
        """
        data = {
            "name": "Test",
            "email": "email@email.com",
            "phone": "1112345678",
            "country": "BR"
        }

        client = APIClient()
        response = client.post(
            reverse("lead"),
            data=data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(
            Lead.objects.filter(channel__slug="default").count(), 1
        )
        self.assertEqual(
            Lead.objects.filter(channel__slug="test-channel").count(), 0
        )

        response = client.post(
            reverse("lead"),
            data=data,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )
        self.assertEqual(
            Lead.objects.filter(channel__slug="default").count(), 1
        )
        self.assertEqual(
            Lead.objects.filter(channel__slug="test-channel").count(), 1
        )

    def test_google_address(self):
        """
        Assert google addresses are saved on the correct channel
        """
        a = GoogleAddress(
            typed_address="Rua Teçaindá, 81, SP",
            typed_address2="Casa"
        )
        a.save(object_channel="test-channel")
