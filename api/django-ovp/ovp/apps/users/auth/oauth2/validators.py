from django.contrib.auth import authenticate
from oauth2_provider.oauth2_validators import (
    OAuth2Validator as OAuth2ValidatorBase
)


class OAuth2Validator(OAuth2ValidatorBase):
    def validate_user(
            self,
            username,
            password,
            client,
            request,
            *args,
            **kwargs):
        """
        Check username and password correspond to a valid and active User
        """
        channel = request.headers.get("Django-request-channel", None)
        u = authenticate(username=username, password=password, channel=channel)
        if u is not None and u.is_active:
            request.user = u
            return True
        return False
