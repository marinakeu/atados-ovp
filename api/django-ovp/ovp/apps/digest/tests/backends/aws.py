# test filter sent recently
# test filter no content
from django.test import TestCase
from django.test import TransactionTestCase
from django.core import mail
from django.db.models import Value, IntegerField
from ovp.apps.channels.models import Channel
from ovp.apps.digest.digest import ContentGenerator
from ovp.apps.digest.digest import DigestCampaign
from ovp.apps.digest.backends.aws import AWSBackend
from ovp.apps.digest.models import DigestLog
from ovp.apps.search.tests.test_views import create_sample_projects
from ovp.apps.search.tests.test_views import create_sample_users
from ovp.apps.users.models import User


class AWSBackendTestCase(TestCase):
    def setUp(self):
        Channel.objects.create(name="Test channel", slug="test-channel")
        create_sample_projects()
        create_sample_users()
        DigestLog.objects.all().delete()

    def test_send_campaign(self):
        User.objects.create(
            email="test@leonardoarroyo.com",
            object_channel="default")
        User.objects.create(
            email="test2@leonardoarroyo.com",
            object_channel="default")
        users = ["test@leonardoarroyo.com", "test2@leonardoarroyo.com"]

        campaign = DigestCampaign(backend=AWSBackend)
        campaign.cg = ContentGenerator(threaded=False)
        out = campaign.send_campaign(email_list=users)
        print(out)

        self.assertEqual(out[0]['Success'], 2)
