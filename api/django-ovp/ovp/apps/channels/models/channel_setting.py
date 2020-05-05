from django.db import models
from django.utils.translation import ugettext_lazy as _
from ovp.apps.channels.models.abstract import ChannelRelationship


class ChannelSetting(ChannelRelationship):
    key = models.CharField(_('Key'), max_length=100)
    value = models.TextField(_('Value'))
