from django import forms
from django.db import models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import TabularInline
from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.gallery.models import Gallery

from martor.widgets import AdminMartorWidget


class UploadedImageInline(TabularInline):
    model = Gallery.images.through
    exclude = ['channel']
    readonly_fields = ['download_link']
    verbose_name = "Image"
    verbose_name_plural = "Images"

    def download_link(self, instance):
        url = instance.uploadedimage.image.url
        return format_html('<a href="{}" target="_blank">Download</a>', url)


class GalleryAdmin(ChannelModelAdmin):
    fields = [
        'id',
        'uuid',
        'name',
        'description',
        'owner',
        'images',
        (
            'created_date',
            'modified_date'
        )
    ]

    list_display = ['id', 'uuid', 'name']

    list_filter = []

    list_editable = []

    search_fields = ['id', 'content']

    readonly_fields = ['id', 'uuid', 'created_date', 'modified_date']

    raw_id_fields = []

    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    inlines = [UploadedImageInline]

    def post(self, obj):
        return obj.__str__()


admin_site.register(Gallery, GalleryAdmin)
