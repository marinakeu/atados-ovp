from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.channels.admin import TabularInline
from ovp.apps.projects.models import Work


class WorkAdmin(ChannelModelAdmin):
    fields = [
        ('id', 'project'),
        'weekly_hours',
        'description',
        'can_be_done_remotely',
    ]

    list_display = [
        'id',
        'project',
        'weekly_hours',
        'can_be_done_remotely'
    ]

    list_editable = []
    search_fields = ['project__name', 'project__organization__name']
    readonly_fields = ['id']
    raw_id_fields = []


class WorkInline(TabularInline):

    model = Work
    exclude = ['channel']


admin_site.register(Work, WorkAdmin)
