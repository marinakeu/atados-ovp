from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CatalogueConfig(AppConfig):
    name = 'ovp.apps.catalogue'
    verbose_name = _('Catalogue')
