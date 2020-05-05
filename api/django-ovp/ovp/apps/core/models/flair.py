from ovp.apps.channels.models.abstract import ChannelRelationship

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Flair(ChannelRelationship):
    name = models.CharField(_('name'), max_length=100)
    value = models.CharField(_('value'), max_length=100, blank=True, null=True)
    image = models.ForeignKey(
        'uploads.UploadedImage',
        blank=True,
        null=True,
        verbose_name=_('image'),
        on_delete=models.DO_NOTHING
    )

    class Meta:
        app_label = 'core'
        verbose_name = _('flair')

    def __str__(self):
        return self.name
