from django.test import TestCase
from django.core.cache import cache
from ovp.apps.channels.models.channel_setting import ChannelSetting
from ovp.apps.channels.cache import get_channel
from ovp.apps.channels.cache import get_channel_setting


class ChannelCacheTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_channel_cache(self):
        with self.assertNumQueries(2):
            channel = get_channel("default")
        with self.assertNumQueries(0):
            channel = get_channel("default")

    def test_channel_cache_settings(self):
        ChannelSetting.objects.all().delete()
        ChannelSetting.objects.create(
            key="test-setting",
            value="test-val",
            object_channel="default"
        )
        ChannelSetting.objects.create(
            key="test-setting2",
            value="test-val",
            object_channel="default"
        )

        with self.assertNumQueries(2):
            channel = get_channel("default")
        with self.assertNumQueries(0):
            channel = get_channel("default")

        self.assertTrue(len(channel["settings"]) == 2)

    def test_channel_settings_function(self):
        self.assertEqual(get_channel_setting("default", "CLIENT_URL"), [""])

        ChannelSetting.objects.create(
            key="CLIENT_URL",
            value="www.test.com",
            object_channel="default"
        )

        cache.clear()
        self.assertEqual(
            get_channel_setting("default", "CLIENT_URL"), ["www.test.com"]
        )
