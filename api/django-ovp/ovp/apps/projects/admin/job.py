from django import forms
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.channels.admin import TabularInline
from ovp.apps.projects.models import Job, JobDate

from .jobdate import JobDateAdmin, JobDateInline

from ovp.apps.core.mixins import CountryFilterMixin


class JobInline(TabularInline):
    exclude = ['title', 'channel', 'can_be_done_remotely']
    readonly_fields = ['admin_link', 'start_date', 'end_date']
    model = Job
    verbose_name = _('Job')
    verbose_name_plural = _('Job')

    def admin_link(self, instance):
        if instance.id is None:
            url = reverse(
                'admin:{0}_{1}_add'.format(
                    instance._meta.app_label,
                    instance._meta.model_name
                )
            )
            return format_html('<a href="{}">Create</a>', url)
        else:
            url = reverse(
                'admin:{0}_{1}_change'.format(
                    instance._meta.app_label,
                    instance._meta.model_name
                ),
                args=(instance.id,)
            )
            return format_html('<a href="{}">Edit</a>', url)


class JobAdmin(ChannelModelAdmin, CountryFilterMixin):

    list_display = ['id', 'project', 'start_date', 'end_date']
    search_fields = ['id', 'project__name', 'project__nonprofit__name']
    exclude = ['channel']
    readonly_fields = ['start_date', 'end_date']

    inlines = (
        JobDateInline,
    )

    def get_queryset(self, request):
        qs = super(JobAdmin, self).get_queryset(request)
        return self.filter_by_country(request, qs, 'project__address')


admin_site.register(Job, JobAdmin)
