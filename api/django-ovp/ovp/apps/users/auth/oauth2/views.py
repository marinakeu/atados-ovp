from rest_framework import response
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework_social_oauth2.views import TokenView as BaseTokenView
from rest_framework_social_oauth2.views import (
    RevokeTokenView as BaseRevokeTokenView
)
from rest_framework_social_oauth2.views import (
    ConvertTokenView as BaseConvertTokenView
)
from rest_framework_social_oauth2.views import (
    invalidate_sessions as base_invalidate_sessions
)
from rest_framework_social_oauth2.oauth2_backends import KeepRequestCore
from drf_yasg.utils import swagger_auto_schema
from ovp.apps.users.auth.oauth2 import serializers
from ovp.apps.users.auth.backends import UserDeactivatedException
from .validators import OAuth2Validator
from .oauthlib_core import KeepRequestChannel


class TokenView(BaseTokenView):
    validator_class = OAuth2Validator
    oauthlib_backend_class = KeepRequestChannel

    @swagger_auto_schema(
        request_body=serializers.RequestTokenViewSerializer,
        responses={
            200: serializers.ResponseTokenViewSerializer,
            401: 'Unauthorized'})
    def post(self, *args, **kwargs):
        """ Exchange authentication credentials for authentication token. """
        try:
            return super().post(*args, **kwargs)
        except UserDeactivatedException as e:
            return response.Response(e.response, status=401)



class RevokeTokenView(BaseRevokeTokenView):
    @swagger_auto_schema(
        request_body=serializers.RequestRevokeTokenViewSerializer,
        responses={
            204: "No content."})
    def post(self, *args, **kwargs):
        """ Revoke an access token. """
        return super().post(*args, **kwargs)


class ConvertTokenView(BaseConvertTokenView):
    @swagger_auto_schema(
        request_body=serializers.RequestConvertTokenViewSerializer,
        responses={
            200: serializers.ResponseConvertTokenViewSerializer,
            401: 'Unauthorized'})
    def post(self, *args, **kwargs):
        """
        Exchange social oauth token(Facebook or Google)
        for a local authentication token.
        """
        try:
            return super().post(*args, **kwargs)
        except UserDeactivatedException as e:
            return response.Response(e.response, status=401)
