from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.channels.admin import TabularInline
from ovp.apps.projects.models import JobDate


class JobDateInline(TabularInline):

    model = JobDate
    exclude = ['channel']
    fields = ['name', 'start_date', 'end_date']
    verbose_name = _('Job Date')
    verbose_name_plural = _('Job Dates')


class JobDateAdmin(ChannelModelAdmin):

    list_display = ['id', 'start_date', 'end_date']
    raw_id_fields = ['job']
    exclude = ['channel']


admin_site.register(JobDate, JobDateAdmin)
