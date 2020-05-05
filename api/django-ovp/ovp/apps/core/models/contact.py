from ovp.apps.channels.models.abstract import ChannelRelationship

from django.db import models
from django.utils.translation import ugettext_lazy as _


class ChannelContact(ChannelRelationship):
    email = models.EmailField(_('Email'), max_length=200)
