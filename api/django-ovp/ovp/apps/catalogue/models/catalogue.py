from django.db import models
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.models.abstract import ChannelRelationship


class Catalogue(ChannelRelationship):
    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'catalogue'
        verbose_name = _('catalogue')
        verbose_name_plural = _('catalogues')
        unique_together = (('slug', 'channel'), )
