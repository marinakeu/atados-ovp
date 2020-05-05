from django.db import models


class ChannelContentFlow(models.Model):
    source = models.ForeignKey('channels.Channel', related_name='flow_source')
    destination = models.ForeignKey(
        'channels.Channel',
        related_name='flow_destination'
    )
