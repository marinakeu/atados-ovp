from django.db import models
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.models.abstract import ChannelRelationship


POSSIBLE_TYPES = (
    ("company", "Company"),
    ("nonprofit", "Nonprofit"),
)


class Lead(ChannelRelationship):
    name = models.CharField(_('Name'), max_length=100, null=True, blank=True)
    email = models.CharField(_('Email'), max_length=100)
    phone = models.CharField(_('Phone'), max_length=30, null=True, blank=True)
    country = models.CharField(
        _('Country'),
        max_length=2,
        null=True,
        blank=True
    )
    city = models.CharField(_('City'), max_length=100, null=True, blank=True)
    date = models.DateTimeField(
        _('Date'),
        auto_now_add=True,
        null=True,
        blank=True
    )
    type = models.CharField(
        max_length=10,
        choices=POSSIBLE_TYPES,
        default='',
        null=True,
        blank=True
    )
    employee_number = models.IntegerField(
        _('Employee number'), default=0, null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = _('Lead')
        verbose_name_plural = _('Leads')
