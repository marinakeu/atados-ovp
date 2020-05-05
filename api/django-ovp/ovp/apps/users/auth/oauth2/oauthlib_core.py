
from __future__ import unicode_literals

from rest_framework_social_oauth2.oauth2_backends import KeepRequestCore


class KeepRequestChannel(KeepRequestCore):
    """
    Subclass of OAuthLibCore used only for the sake of keeping the django
    request channel by placing it in the headers.

    This is a hack similar to rest_framework_social_oauth2 KeepRequestCore
    which should have suficed, but the header ends up empty for some reason.
    """

    def _extract_params(self, request):
        uri, http_method, body, headers = super(
            KeepRequestChannel, self)._extract_params(request)
        headers["Django-request-channel"] = request.channel
        return uri, http_method, body, headers
