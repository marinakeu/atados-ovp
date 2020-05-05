from ovp.apps.core.emails import BaseMail


class DigestEmail(BaseMail):
    """
    This class is responsible for firing emails for digest messages
    """

    def __init__(self, email, channel, async_mail=None):
        super().__init__(
            email,
            channel=channel,
            async_mail=async_mail
        )

    def sendDigest(self, context={}):
        """
        Sent when user should receive a news digest
        """
        return self.sendEmail('userDigest', 'New projects for you', context)
