from ovp.apps.channels.viewsets.decorators import ChannelViewSet
from ovp.apps.digest.models import DigestLog
from ovp.apps.users.models import User

from rest_framework import viewsets
from rest_framework import response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema


@ChannelViewSet
class DigestViewSet(viewsets.GenericViewSet):
    """
    Digest resource endpoint
    """
    lookup_field = 'uuid'
    queryset = DigestLog.objects.all()

    @swagger_auto_schema(responses={200: 'OK'})
    @action(methods=['POST'], detail=True, url_path='cancel')
    def cancel(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            user = User.objects.get(email__iexact=obj.recipient, channel=obj.channel)
        except User.DoesNotExist:
            return response.Response({"detail": "Invalid user."}, status=400)

        if not user.is_subscribed_to_newsletter:
            return response.Response(
                {"detail": "User not subscribed to newsletter."})

        user.is_subscribed_to_newsletter = False
        user.save()
        return response.Response(
            {"detail": "User unsubscribed from newsletter."}
        )
