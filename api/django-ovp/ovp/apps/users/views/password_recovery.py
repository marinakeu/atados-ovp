from .generic_token import GenericUserTokenViewSet
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

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
class RecoveryTokenViewSet(GenericUserTokenViewSet):
    """
    RecoveryToken resource endpoint
    """
    queryset = models.User.objects.filter(is_active=True)
    serializer_class = serializers.RecoveryTokenSerializer
    Token = models.PasswordRecoveryToken


@ChannelViewSet
class RecoverPasswordViewSet(viewsets.GenericViewSet):
    """
    RecoverPassword resource endpoint
    """
    queryset = models.PasswordRecoveryToken.objects.all()
    serializer_class = serializers.RecoverPasswordSerializer

    @swagger_auto_schema(
        responses={
            200: 'OK',
            400: 'Bad request',
            401: 'Unauthorized'})
    def create(self, request, *args, **kwargs):
        """ Update user password using recovery token. """
        token = request.data.get('token', None)
        new_password = request.data.get('new_password', None)
        day_ago = (
            timezone.now() -
            relativedelta(
                hours=24)).replace(
            tzinfo=timezone.utc)

        try:
            rt = self.get_queryset().get(token=token)
        except BaseException:
            rt = None

        if (not rt) or rt.used_date or rt.created_date < day_ago:
            return response.Response(
                {'message': 'Invalid token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not new_password:
            return response.Response(
                {'message': 'Empty password not allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user=rt.user)
        except ValidationError as e:
            errors = list(map(lambda x: [x.code, x.message], e.error_list))
            return response.Response(
                {'message': 'Invalid password.', 'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializers.RecoverPasswordSerializer(
            data=request.data,
            context=self.get_serializer_context()
        ).is_valid(raise_exception=True)

        rt.used_date = timezone.now()
        rt.save()

        rt.user.password = new_password
        rt.user.save()

        return response.Response({'message': 'Password updated.'})
