from django.test import TestCase
from django.core import mail
from django.utils import translation

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.channels.content_flow import CFM
from ovp.apps.channels.models import Channel
from ovp.apps.core import models
from ovp.apps.core import serializers


class TestStartupView(TestCase):
    def setUp(self):
        with translation.override('en'):
            self.skills_data = serializers.SkillSerializer(
                CFM.filter_queryset(
                    "default",
                    models.Skill.objects.all().order_by('pk')
                ), many=True
            ).data
            self.causes_data = serializers.FullCauseSerializer(
                CFM.filter_queryset(
                    "default",
                    models.Cause.objects.all().order_by('pk')
                ), many=True
            ).data

    def test_returns_startup_data(self):
        """
        Test startup route returns skills and causes
        """
        client = APIClient()
        response = client.get(reverse("startup"), format="json")

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["skills"] == self.skills_data)
        self.assertTrue(response.data["causes"] == self.causes_data)

    def test_returns_localized_startup_data(self):
        """
        Test startup route returns skills and causes
        """
        client = APIClient(HTTP_ACCEPT_LANGUAGE="pt-br")
        response = client.get(reverse("startup"), format="json")

        with translation.override('pt-br'):
            skills_data = serializers.SkillSerializer(
                CFM.filter_queryset(
                    "default",
                    models.Skill.objects.all().order_by('pk')
                ), many=True
            ).data
            causes_data = serializers.FullCauseSerializer(
                CFM.filter_queryset(
                    "default",
                    models.Cause.objects.all().order_by('pk')
                ), many=True
            ).data
            self.assertTrue(response.status_code == 200)
            self.assertTrue(response.data["skills"] == skills_data)
            self.assertTrue(response.data["causes"] == causes_data)

    def test_content_flow(self):
        Channel.objects.create(name="Test channel", slug="test-channel")

        client = APIClient()
        response = client.get(reverse("startup"), format="json")
        len_skills = len(response.data["skills"])
        len_causes = len(response.data["causes"])

        self._add_contentflow()
        response = client.get(reverse("startup"), format="json")
        self.assertEqual(len(response.data["skills"]), len_skills * 2)
        self.assertEqual(len(response.data["causes"]), len_causes * 2)

    def _add_contentflow(self):
        from ovp.apps.channels.content_flow import BaseContentFlow
        from ovp.apps.channels.content_flow import NoContentFlow
        from ovp.apps.channels.content_flow import CFM
        from django.db.models import Q
        from haystack.query import SQ

        class Flow:
            source = "test-channel"
            destination = "default"

            def get_filter_queryset_q_obj(self, model_class):
                if model_class in [models.Cause, models.Skill]:
                    return Q()

                raise NoContentFlow

            def get_filter_searchqueryset_q_obj(self, model_class):
                if model_class in [models.Cause, models.Skill]:
                    return SQ()

                raise NoContentFlow

        CFM.add_flow(Flow())


class TestContactFormView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.basis_data = {
            "name": "my-name",
            "message": "my message",
            "email": "reply_to@asddsa.com",
            "phone": "+5511912345678"
        }

    def test_cant_send_invalid_recipient(self):
        """
        Test sending contact form to invalid recipient does not work
        """
        data = self.basis_data

        data["recipients"] = ["invalid@recipient.com"]
        response = self.client.post(
            reverse("contact"),
            data=data,
            format="json"
        )
        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data["detail"] == "Invalid recipients.")
        self.assertTrue(len(mail.outbox) == 0)

        data["recipients"] = ["testemail@1.com", "invalid@recipient.com"]
        response = self.client.post(
            reverse("contact"),
            data=data,
            format="json"
        )
        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data["detail"] == "Invalid recipients.")
        self.assertTrue(len(mail.outbox) == 0)

    def test_can_send_valid_recipient(self):
        """
        Test sending contact form to valid recipient does work
        """
        data = self.basis_data
        data["recipients"] = ["testemail@1.com"]
        models.ChannelContact.objects.create(
            email="testemail@1.com",
            object_channel="default"
        )

        response = self.client.post(
            reverse("contact"),
            data=data,
            format="json"
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(mail.outbox) == 1)
        self.assertTrue(data["name"] in mail.outbox[0].body)
        self.assertTrue(data["message"] in mail.outbox[0].body)
        self.assertTrue(data["email"] in mail.outbox[0].body)
        self.assertTrue(data["phone"] in mail.outbox[0].body)

    def test_can_send_multiple_valid_recipients(self):
        """
        Test sending contact form to multiple valid recipient does work
        """
        data = self.basis_data
        data["recipients"] = ["testemail@1.com", "testemail@2.com"]
        models.ChannelContact.objects.create(
            email="testemail@1.com",
            object_channel="default"
        )
        models.ChannelContact.objects.create(
            email="testemail@2.com",
            object_channel="default"
        )

        response = self.client.post(
            reverse("contact"),
            data=data,
            format="json"
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(mail.outbox) == 2)
