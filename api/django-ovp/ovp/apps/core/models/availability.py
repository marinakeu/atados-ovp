from ovp.apps.channels.models import ChannelRelationship

from django.db import models
from django.utils.translation import ugettext_lazy as _


AVAILABILITY_PERIODS = (
    (0, 'Manhã'),
    (1, 'Tarde'),
    (2, 'Noite')
)


AVAILABILITY_WEEKDAYS = (
    (0, 'Domingo'),
    (1, 'Segunda'),
    (2, 'Terça'),
    (3, 'Quarta'),
    (4, 'Quinta'),
    (5, 'Sexta'),
    (6, 'Sábado')
)


class Availability(ChannelRelationship):
    weekday = models.PositiveSmallIntegerField(
        _('Weekday'),
        choices=AVAILABILITY_WEEKDAYS,
        default=0
    )
    period = models.PositiveSmallIntegerField(
        _('Day period'),
        choices=AVAILABILITY_PERIODS,
        default=0
    )
    period_index = models.PositiveSmallIntegerField(db_index=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.period_index = __class__.compose_period_index_for(
                self.weekday,
                self.period
            )

    def __str__(self):
        return "{} de {}".format(
            self.get_weekday_display(),
            self.get_period_display()
        )

    @staticmethod
    def compose_period_index_for(weekday, period):
        return int(weekday) * len(AVAILABILITY_WEEKDAYS) + int(period)

    @staticmethod
    def decompose_period_index(index):
        weekday_count = len(AVAILABILITY_WEEKDAYS)
        return int(index / weekday_count), index % weekday_count
