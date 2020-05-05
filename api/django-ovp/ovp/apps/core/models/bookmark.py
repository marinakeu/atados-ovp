from django.db import models
from ovp.apps.channels.models.abstract import ChannelRelationship


class AbstractBookmark(ChannelRelationship):
    user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING)
    subscription = models.BooleanField(default=False)

    class Meta:
        abstract = True
