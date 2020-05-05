from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.channels.admin import TabularInline
from ovp.apps.core.models import Cause


class CauseInline(TabularInline):
    model = Cause


class CauseAdmin(ChannelModelAdmin):
    list_filter = []
    fields = ['id', 'name', 'image', 'slug']
    list_display = ['id', 'name']
    list_editable = []
    search_fields = ['id', 'name']
    readonly_fields = ['id']


admin_site.register(Cause, CauseAdmin)
