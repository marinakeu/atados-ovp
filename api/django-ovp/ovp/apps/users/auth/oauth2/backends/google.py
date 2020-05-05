from social_core.backends.google import GoogleOAuth2 as GoogleOAuth2Base
from rest_framework.exceptions import AuthenticationFailed


class GoogleOAuth2(GoogleOAuth2Base):
    def auth_allowed(self, response, details):
        if not response.get("email_verified", False):
            raise AuthenticationFailed({
                "error": "access_denied",
                "error_description": "Your email is not verified "
                                     "by the provider"
            })
        return super(GoogleOAuth2, self).auth_allowed(response, details)

    def get_user_details(self, response):
        data = super(GoogleOAuth2, self).get_user_details(response)
        return {
            'email': data['email'],
            'name': data['fullname']
        }

    def user_data(self, access_token, *args, **kwargs):
        """Return user data from Google API"""
        data = super(
            GoogleOAuth2,
            self).user_data(
            access_token,
            *
            args,
            **kwargs)
        tokeninfo = self.get_json(
            'https://www.googleapis.com/oauth2/v3/tokeninfo',
            params={
                'access_token': access_token,
                'alt': 'json'
            }
        )
        data["email_verified"] = tokeninfo["email_verified"] == "true"
        return data

    def get_key_and_secret(self):
        url = self.strategy.request.META['HTTP_HOST']
        keys = json.loads(os.environ.get('GOOGLE_KEYS', "{}"))
        return keys.get(
            self.strategy.request.channel,
            (self.setting('KEY'),
             self.setting('SECRET')))
