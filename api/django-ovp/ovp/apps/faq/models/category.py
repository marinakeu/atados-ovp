from django.db import models
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.models.abstract import ChannelRelationship


class FaqCategory(ChannelRelationship):
    name = models.CharField(_('Name'), max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'faq'
        verbose_name = _('faq category')
        verbose_name_plural = _('faq categories')
