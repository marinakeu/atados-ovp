from django import forms

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.faq.models import Faq


class FaqAdmin(ChannelModelAdmin):
    list_display = ['id', 'question']
    fields = ['category', 'question', 'answer', 'language']
    search_fields = [
        'question'
    ]


admin_site.register(Faq, FaqAdmin)
