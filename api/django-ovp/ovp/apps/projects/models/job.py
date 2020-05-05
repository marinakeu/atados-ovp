from django.db import models
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.models.abstract import ChannelRelationship


class JobDate(ChannelRelationship):

    name = models.CharField(_('Label'), blank=True, null=True, max_length=20)
    start_date = models.DateTimeField(_('Start date'))
    end_date = models.DateTimeField(_('End date'))
    job = models.ForeignKey(
        'Job',
        models.CASCADE,
        blank=True,
        null=True,
        related_name='dates',
        verbose_name=_('job'),
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.job:
            self.job.update_dates()

    def __str__(self):
        start_date_str = self.start_date.strftime("%d/%m/%Y %T")
        start_date = self.start_date and start_date_str or '#'

        end_date_str = self.end_date.strftime("%d/%m/%Y %T")
        end_date = self.end_date and end_date_str or '#'
        return "{}: {} ~ {}".format(self.name, start_date, end_date)

    class Meta:
        app_label = 'projects'
        verbose_name = _('job date')
        verbose_name_plural = _('job dates')


class Job(ChannelRelationship):

    project = models.OneToOneField('Project', blank=True, null=True, on_delete=models.DO_NOTHING)
    start_date = models.DateTimeField(_('Start date'), blank=True, null=True)
    end_date = models.DateTimeField(_('End date'), blank=True, null=True)
    can_be_done_remotely = models.BooleanField(
        _('This job can be done remotely'),
        default=False
    )

    def __str__(self):
        name = self.project and self.project.name or _('Unbound Job')
        start_date_str = self.start_date.strftime("%d/%m/%Y")
        start_date = self.start_date and start_date_str or ''
        end_date = self.end_date and self.end_date.strftime("%d/%m/%Y") or ''
        return "{}: {} ~ {}".format(name, start_date, end_date)

    def save(self, *args, **kwargs):
        self.update_dates(save=False)
        super().save(*args, **kwargs)

    def update_dates(self, save=True):
        start = self.dates.all().order_by('start_date').first()
        end = self.dates.all().order_by('-end_date').first()

        if start:
            self.start_date = start.start_date
        if end:
            self.end_date = end.end_date

        if save:
            self.save()

    class Meta:
        app_label = 'projects'
        verbose_name = _('job')
        verbose_name_plural = _('jobs')
