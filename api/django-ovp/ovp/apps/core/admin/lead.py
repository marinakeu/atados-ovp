from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

import csv
from django.http import HttpResponse

from ovp.apps.admin.resources import CleanModelResource
from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.core.models import Lead

from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field


def export_all_as_csv(model_admin, request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads.csv"'

    csv_writer = csv.writer(response)
    for lead in queryset.all():
        csv_writer.writerow(
            [
                lead.email,
                lead.name or '',
                lead.phone or '',
                lead.country or ''
            ]
        )

    return response


class LeadResource(CleanModelResource):

    class Meta:
        model = Lead
        fields = ('name', 'email', 'phone', 'city', 'type', 'employee_number')


class LeadAdmin(ImportExportModelAdmin, ChannelModelAdmin):
    fields = ['id', 'name', 'email', 'phone', 'type', 'employee_number']
    list_display = ['id', 'name', 'email', 'phone', 'type']
    list_filter = []
    list_editable = []
    search_fields = ['id', 'name', 'email', 'phone', 'type']
    readonly_fields = ['id']
    raw_id_fields = []

    resource_class = LeadResource

    actions = [export_all_as_csv]

    def changelist_view(self, request, extra_context=None):
        if ('action' in request.POST and
                request.POST['action'] == 'export_all_as_csv'):
            # Make a list with all ids to make a 'export all'
            if not request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Lead.objects.all():
                    post.update({admin.ACTION_CHECKBOX_NAME: str(u.id)})
                request._set_post(post)
        return super().changelist_view(request, extra_context)


admin_site.register(Lead, LeadAdmin)
