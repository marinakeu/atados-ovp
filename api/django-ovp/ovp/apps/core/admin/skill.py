from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.channels.admin import TabularInline
from ovp.apps.core.models import Skill


class SkillInline(TabularInline):
    model = Skill


class SkillAdmin(ChannelModelAdmin):
    fields = ['id', 'name', 'slug']
    list_display = ['id', 'name']
    list_filter = []
    list_editable = []
    search_fields = ['id', 'name']
    readonly_fields = ['id']
    raw_id_fields = []


admin_site.register(Skill, SkillAdmin)
