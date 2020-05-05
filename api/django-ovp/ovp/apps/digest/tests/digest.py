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


class DigestTestCase(TestCase):
    def setUp(self):
        Channel.objects.create(name="Test channel", slug="test-channel")
        create_sample_projects()
        create_sample_users()
        DigestLog.objects.all().delete()

    def test_num_queries_generate_content(self):
        user = User.objects.annotate(campaign=Value(0, IntegerField()))
        user = user.select_related('channel', 'users_userprofile_profile')
        user = user.get(email="testmail1@test.com")

        cg = ContentGenerator()
        with self.assertNumQueries(2):
            content = cg.generate_content_for_user(user)

        self.assertEqual(len(content['projects']), 2)

    def test_digest_log(self):
        """ Assert sending a email register digest log """
        # Test creates digest log
        pass
