from multiprocessing.dummy import Pool as ThreadPool
from ovp.apps.digest.emails import DigestEmail
from ovp.apps.digest.models import PROJECT
from ovp.apps.digest.backends.base import BaseBackend


class SMTPBackend(BaseBackend):
    def __init__(self, channel, threaded=True):
        super().__init__(channel)
        self.threaded = threaded

    def send_email(self, v):
        recipient = v["email"]
        channel = v["channel"]

        v["uuid"] = self.create_digest_log(v)
        DigestEmail(recipient, channel, async_mail=False).sendDigest(v)

        print(".", end="", flush=True)

    def send_chunk(self, content, template_context={}):
        if self.threaded:
            self.send_chunk_threaded(content, template_context)
        else:
            self.send_chunk_sync(content, template_context)

    def send_chunk_threaded(self, content, template_context):
        pool = ThreadPool(1)
        result = pool.map(self.send_email, content)
        print("")

    def send_chunk_sync(self, content, template_context):
        for item in content:
            self.send_email(item)
