# test filter sent recently
# test filter no content
from django.test import TestCase
from django.test import TransactionTestCase
from django.core import mail
from django.db.models import Value, IntegerField
from ovp.apps.channels.models import Channel
from ovp.apps.digest.digest import ContentGenerator
from ovp.apps.digest.digest import DigestCampaign
from ovp.apps.digest.models import DigestLog
from ovp.apps.search.tests.test_views import create_sample_projects
from ovp.apps.search.tests.test_views import create_sample_users
from ovp.apps.users.models import User


class SMTPBackendTestCase(TransactionTestCase):
    def setUp(self):
        Channel.objects.create(name="Test channel", slug="test-channel")
        create_sample_projects()
        create_sample_users()
        DigestLog.objects.all().delete()

    def test_send_campaign(self):
        users = ["testmail1@test.com"]

        mail.outbox = []
        self.assertEqual(len(mail.outbox), 0)

        campaign = DigestCampaign(backend_kwargs={'threaded': False})
        campaign.cg = ContentGenerator(threaded=False)
        campaign.send_campaign(email_list=users)

        self.assertEqual(len(mail.outbox), 1)
