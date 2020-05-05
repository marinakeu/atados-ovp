from ovp.apps.digest.digest import ContentGenerator
from ovp.apps.digest.digest import DigestCampaign
from ovp.apps.digest.models import DigestLog
from ovp.apps.digest.backends.aws import AWSBackend
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        campaign_number = self.get_current_campaign()
        campaign = DigestCampaign(backend=AWSBackend, campaign=125)
        sent = set(
            DigestLog.objects.filter(
                campaign__gte=campaign_number).values_list(
                'recipient',
                flat=True))
        all_emails = campaign._get_email_list()
        to_send = filter(lambda x: x not in sent, all_emails)
        campaign.cg = ContentGenerator(threaded=False)
        campaign.send_campaign(chunk_size=1, email_list=to_send)

    def get_current_campaign(self):
        last_log = DigestLog.objects.last()
        if last_log:
            return last_log.campaign
        return 1
