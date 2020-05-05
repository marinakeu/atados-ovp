from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RatingsConfig(AppConfig):
    name = 'ovp.apps.ratings'
    verbose_name = _('Ratings')
