from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProjectsConfig(AppConfig):
    name = 'ovp.apps.projects'
    verbose_name = _('Projects')
