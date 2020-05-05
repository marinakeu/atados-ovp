from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.channels.admin import TabularInline
from ovp.apps.core.models import Post

from martor.widgets import AdminMartorWidget


class PostAdmin(ChannelModelAdmin):

    fields = [
        'id',
        'user',
        'gallery',
        (
            'published',
            'deleted'
        ),
        'content',
        (
            'created_date',
            'modified_date',
            'deleted_date'
        )
    ]

    list_display = [
        'id',
        'post',
        'title',
        'published',
        'deleted'
    ]

    search_fields = [
        'id',
        'content'
    ]

    readonly_fields = ['id', 'created_date', 'modified_date', 'deleted_date']

    raw_id_fields = []

    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    def post(self, obj):
        return obj.__str__()


admin_site.register(Post, PostAdmin)
