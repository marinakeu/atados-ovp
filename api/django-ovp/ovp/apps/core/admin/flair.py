from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.core.models import Flair


class FlairAdmin(ChannelModelAdmin):
    fields = ['id', 'name', 'image', 'value']
    list_display = ['id', 'name']
    list_editable = []
    search_fields = ['id', 'name']
    readonly_fields = ['id']


admin_site.register(Flair, FlairAdmin)
