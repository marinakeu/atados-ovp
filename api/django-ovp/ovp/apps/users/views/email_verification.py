from .generic_token import GenericUserTokenViewSet
from django.utils import timezone

from dateutil.relativedelta import relativedelta

from ovp.apps.users import serializers
from ovp.apps.users import models

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema


@ChannelViewSet
class RequestEmailVerificationViewSet(GenericUserTokenViewSet):
    """
    RecoveryToken resource endpoint
    """
    queryset = models.User.objects.filter(is_active=True)
    serializer_class = serializers.RecoveryTokenSerializer
    Token = models.EmailVerificationToken

    @swagger_auto_schema(responses={200: 'OK', 429: 'Too many requests.'})
    def create(self, *args, **kwargs):
        result = super().create(*args, **kwargs)

        if result.status_code == 200:
            return response.Response(
                {'success': True, 'message': 'Token requested successfully.'}
            )

        return result


@ChannelViewSet
class VerificateEmailViewSet(viewsets.GenericViewSet):
    """
    Verificate email resource endpoint
    """
    queryset = models.EmailVerificationToken.objects.all()
    serializer_class = serializers.EmailVerificationSerializer

    @swagger_auto_schema(
        responses={
            200: 'OK',
            400: 'Bad request',
            401: 'Unauthorized'})
    def create(self, request, *args, **kwargs):
        """ Update user password using recovery token. """
        token = request.data.get('token', None)
        day_ago = (
            timezone.now() -
            relativedelta(
                hours=24)).replace(
            tzinfo=timezone.utc)

        try:
            vt = self.get_queryset().get(token=token)
        except BaseException:
            vt = None

        if (not vt) or vt.used_date or vt.created_date < day_ago:
            return response.Response(
                {'message': 'Invalid token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializers.EmailVerificationSerializer(
            data=request.data,
            context=self.get_serializer_context()).is_valid(
            raise_exception=True
        )

        vt.used_date = timezone.now()
        vt.save()

        vt.user.is_email_verified = True
        vt.user.save()

        return response.Response({'message': 'Email is now verified.'})
