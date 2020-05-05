from django.utils import timezone

from dateutil.relativedelta import relativedelta

from ovp.apps.users import serializers
from ovp.apps.users import models

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema


@ChannelViewSet
class GenericUserTokenViewSet(viewsets.GenericViewSet):
    """
    Generates generic tokens for users.
    Used by password recovery and email verification.
    """
    queryset = models.User.objects.filter(is_active=True)

    @swagger_auto_schema(responses={200: 'OK', 429: 'Too many requests.'})
    def create(self, request, *args, **kwargs):
        """
        Request a password recovery token. An email will be dispatched
        if the user is registered on the platform.
        """
        if request.user.is_authenticated:
            user = request.user
        else:
            try:
                email = request.data.get('email', None)
                user = self.get_queryset().filter(
                    channel__slug=request.channel
                ).get(email__iexact=email)
            except BaseException:
                user = None

        if user:
            # Allow only 5 requests per hour
            limit = 5
            now = timezone.now()
            to_check = (
                now -
                relativedelta(
                    hours=1)).replace(
                tzinfo=timezone.utc)
            tokens = self.Token.objects.filter(
                user=user,
                created_date__gte=to_check,
                channel__slug=request.channel
            )

            if tokens.count() >= limit:
                will_release = tokens.order_by('-created_date')[limit - 1]
                will_release = will_release.created_date
                will_release += relativedelta(hours=1)
                seconds = abs((will_release - now).seconds)
                return response.Response(
                    {
                        'success': False,
                        'message': 'Five tokens generated last hour.',
                        'try_again_in': seconds
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            token = self.Token.objects.create(
                user=user, object_channel=request.channel)

        return response.Response(
            {
                'success': True,
                'message': 'Token requested successfully(if user exists).'
            }
        )
