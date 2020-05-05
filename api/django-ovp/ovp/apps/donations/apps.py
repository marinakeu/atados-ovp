from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DonationsConfig(AppConfig):
    name = 'ovp.apps.donations'
    verbose_name = _('Donations')
