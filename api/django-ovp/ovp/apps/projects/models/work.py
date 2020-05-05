from django.db import models
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.models.abstract import ChannelRelationship


class Work(ChannelRelationship):

    project = models.OneToOneField('Project', blank=True, null=True, on_delete=models.DO_NOTHING)
    weekly_hours = models.PositiveSmallIntegerField(
        _('Weekly hours'),
        blank=True,
        null=True
    )
    description = models.CharField(
        _('Description'),
        max_length=4000,
        blank=True,
        null=True
    )
    can_be_done_remotely = models.BooleanField(
        _('This job can be done remotely'),
        default=False
    )

    def __str__(self):
        return _('{0} hours per week').format(
            self.weekly_hours if self.weekly_hours else 0
        )

    class Meta:
        app_label = 'projects'
        verbose_name = _('work')
        verbose_name_plural = _('works')
