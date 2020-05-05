from ovp.apps.channels.models import Channel
from ovp.apps.digest.models import DigestLog
from ovp.apps.digest.models import DigestLogContent
from ovp.apps.digest.models import PROJECT


class BaseBackend():
    def __init__(self, channel):
        self.channel = channel

    def create_digest_log(self, data):
        recipient = data["email"]
        channel = data["channel"]
        channel_obj = Channel.objects.get(slug=channel)
        campaign = data["campaign"]

        dlog = DigestLog.objects.create(
            recipient=recipient,
            campaign=campaign,
            object_channel=channel
        )
        objs = [
            DigestLogContent(
                channel=channel_obj,
                content_type=PROJECT,
                content_id=x["pk"],
                digest_log=dlog) for x in data["projects"]]
        DigestLogContent.objects.bulk_create(objs)

        return str(dlog.uuid)

    def send_chunk(self, content_map):
        raise NotImplementedError

    def send_email(self, data):
        raise NotImplementedError
