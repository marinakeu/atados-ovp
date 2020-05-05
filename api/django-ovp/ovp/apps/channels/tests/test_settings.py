from django.test import TestCase
from django.core.cache import cache

from ovp.apps.channels.models.channel import Channel
from ovp.apps.channels.models.channel_setting import ChannelSetting
from ovp.apps.channels.cache import get_channel

from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class ChannelSettingsTestCase(TestCase):
    def setUp(self):
        Channel.objects.create(slug="test-one", name="Test one")
        Channel.objects.create(slug="test-two", name="Test two")
        cache.clear()

#  This test is commented out. Please check ovp.apps.channels.signals for more information.
#  def test_cors(self):
#    ChannelSetting.objects.create(key="CORS_ORIGIN_WHITELIST", value="default.com", object_channel="default")
#    ChannelSetting.objects.create(key="CORS_ORIGIN_WHITELIST", value="www.default.com", object_channel="default")
#    ChannelSetting.objects.create(key="CORS_ORIGIN_WHITELIST", value="test.com", object_channel="test-one")
#
#    response = self.client.get(reverse("test-projects-list"), format="json", HTTP_X_OVP_CHANNEL="default", HTTP_ORIGIN="http://default.com")
#    self.assertEqual("http://default.com", response.get("Access-Control-Allow-Origin"))
#
#    response = self.client.get(reverse("test-projects-list"), format="json", HTTP_X_OVP_CHANNEL="default", HTTP_ORIGIN="http://www.default.com")
#    self.assertEqual("http://www.default.com", response.get("Access-Control-Allow-Origin"))
#
#    response = self.client.get(reverse("test-projects-list"), format="json", HTTP_X_OVP_CHANNEL="default", HTTP_ORIGIN="http://invalid.com")
#    self.assertEqual(None, response.get("Access-Control-Allow-Origin", None))
#
#    response = self.client.get(reverse("test-projects-list"), format="json", HTTP_X_OVP_CHANNEL="default", HTTP_ORIGIN="http://test.com")
#    self.assertEqual(None, response.get("Access-Control-Allow-Origin", None))
#
#    response = self.client.get(reverse("test-projects-list"), format="json", HTTP_X_OVP_CHANNEL="test-one", HTTP_ORIGIN="http://test.com")
#    self.assertEqual("http://test.com", response.get("Access-Control-Allow-Origin"))
#
#    response = self.client.get(reverse("test-projects-list"), format="json", HTTP_X_OVP_CHANNEL="test-one", HTTP_ORIGIN="http://invalid.com")
#    self.assertEqual(None, response.get("Access-Control-Allow-Origin", None))
#
#    response = self.client.get(reverse("test-projects-list"), format="json", HTTP_X_OVP_CHANNEL="test-two", HTTP_ORIGIN="http://invalid.com")
#    self.assertEqual(None, response.get("Access-Control-Allow-Origin", None))
