from django import forms

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.faq.models import FaqCategory


class FaqCategoryAdmin(ChannelModelAdmin):
    list_display = ['id', 'name']
    fields = ['name']


admin_site.register(FaqCategory, FaqCategoryAdmin)
