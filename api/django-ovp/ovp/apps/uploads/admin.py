from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.uploads.models import UploadedImage
from ovp.apps.uploads.models import UploadedDocument


class UploadedImageAdmin(ChannelModelAdmin):
    fields = [
        'id', 'image', 'image_small', 'image_medium', 'image_large'
    ]

    list_display = [
        'id', 'image', 'user'
    ]

    list_filter = []

    list_editable = []

    search_fields = [
        'id', 'user__name', 'user__email'
    ]

    readonly_fields = [
        'id', 'image_small', 'image_medium', 'image_large'
    ]

    raw_id_fields = [
        'user'
    ]


class UploadedDocumentAdmin(ChannelModelAdmin):
    fields = [
        'id', 'uuid', 'document', 'user', ('created_date', 'modified_date')
    ]

    list_display = [
        'id', 'uuid', 'user'
    ]

    list_filter = []

    list_editable = []

    search_fields = [
        'id', 'user__name', 'user__email'
    ]

    readonly_fields = [
        'id', 'uuid', 'created_date', 'modified_date'
    ]

    raw_id_fields = [
        'user'
    ]


admin_site.register(UploadedDocument, UploadedDocumentAdmin)
admin_site.register(UploadedImage, UploadedImageAdmin)
