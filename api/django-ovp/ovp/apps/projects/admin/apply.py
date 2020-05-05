from django import forms
from django.utils.translation import ugettext_lazy as _
from jet.filters import DateRangeFilter

from ovp.apps.admin.resources import CleanModelResource
from ovp.apps.admin.filters import SingleTextInputFilter
from ovp.apps.organizations.admin import StateListFilter as BaseStateListFilter
from ovp.apps.organizations.admin import CityListFilter as BaseCityListFilter
from ovp.apps.projects.models import Apply
from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.core.mixins import CountryFilterMixin
from ovp.apps.core.models import GoogleAddress
from ovp.apps.core.models import SimpleAddress
from ovp.apps.core.helpers import get_address_model

from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field


class ApplyResource(CleanModelResource):
    project_id = Field(column_name="ID Projeto")
    project = Field(column_name="Projeto")
    organization = Field(column_name="ONG")
    volunteer_id = Field(column_name="ID do Voluntario")
    volunteer_name = Field(column_name="Nome do Voluntario")
    volunteer_email = Field(column_name="Email do Voluntario")
    volunteer_phone = Field(column_name="Telefone do Voluntario")
    volunteer_document = Field(column_name="Documento")
    address = Field(column_name="Endereco do projeto")

    class Meta:
        model = Apply
        fields = (
            'name',
            'volunteer_id',
            'volunteer_name',
            'volunteer_phone',
            'volunteer_email',
            'volunteer_document'
            'status',
            'date',
            'organization',
            'project_id',
            'project'
        )

    def before_export(self, qs, *args, **kwargs):
        return qs.select_related(
            'project__organization',
            'user',
            'project__address'
        )

    def dehydrate_organization(self, apply):
        if (hasattr(apply, 'project')
                and hasattr(apply.project, 'organization')
                and apply.project.organization is not None):
            return apply.project.organization.name
        return ""

    def dehydrate_project(self, apply):
        return apply.project.name

    def dehydrate_project_id(self, apply):
        return apply.project.id

    def dehydrate_address(self, apply):
        if apply.project.address is not None:
            address = apply.project.address
            if isinstance(address, GoogleAddress):
                return address.address_line
            if isinstance(address, SimpleAddress):
                return '{0}, {1} - {2} - {3}'.format(
                    address.street,
                    address.number,
                    address.neighbourhood,
                    address.city
                )

    def dehydrate_volunteer_name(self, apply):
        if apply.user is not None:
            return apply.user.name
        return apply.username

    def dehydrate_volunteer_id(self, apply):
        if apply.user is not None:
            return apply.user.id
        return 0

    def dehydrate_volunteer_email(self, apply):
        if apply.user is not None:
            return apply.user.email
        return apply.email

    def dehydrate_volunteer_phone(self, apply):
        if apply.user is not None:
            return apply.user.phone
        return apply.phone

    def dehydrate_volunteer_document(self, apply):
        if apply.user is not None:
            return apply.user.document
        return apply.document


class StateListFilter(BaseStateListFilter):

    def queryset(self, request, queryset):
        address_model = get_address_model()
        state = request.GET.get('state', None)

        if state:
            if address_model == GoogleAddress:
                return queryset.filter(
                    project__address__address_components__short_name=state,
                    project__address__address_components__types__name="administrative_area_level_1")

            if address_model == SimpleAddress:
                return queryset.filter(project__address__state=state)
        return queryset


class CityListFilter(BaseCityListFilter):

    def queryset(self, request, queryset):
        address_model = get_address_model()
        city = request.GET.get('city', None)

        if city:
            if address_model == GoogleAddress:
                return queryset.filter(
                    project__address__address_components__long_name=city,
                    project__address__address_components__types__name="administrative_area_level_2")

            if address_model == SimpleAddress:
                return queryset.filter(project__address__city=city)
        return queryset


class ApplyAdmin(
        ChannelModelAdmin,
        CountryFilterMixin,
        ImportExportModelAdmin):

    resource_class = ApplyResource

    fields = [
        ('id', 'project__name', 'status'),
        'user', 'project', 'project__organization__name',
        ('canceled_date', 'date'),
        'email',
        'phone',
        'username',
        'document',
        'message'
    ]

    list_display = [
        'id',
        'date',
        'user__name',
        'user__email',
        'user__phone',
        'project__name',
        'project__organization__name',
        'project__address',
        'username',
        'phone',
        'email',
        'status'
    ]

    list_filter = [
        ('date', DateRangeFilter),
        ('project__job__end_date', DateRangeFilter),
        'status',
        StateListFilter,
        CityListFilter
    ]

    list_editable = []

    search_fields = [
        'user__name',
        'user__email',
        'project__pk',
        'project__name',
        'project__organization__name'
    ]

    readonly_fields = [
        'id',
        'project__name',
        'user',
        'project__organization__name',
        'canceled_date',
        'date'
    ]

    raw_id_fields = []

    def user__name(self, obj):
        if obj.user:
            return obj.user.name
        else:
            return obj.username

    user__name.short_description = _('Name')
    user__name.admin_order_field = 'user__name'

    def user__email(self, obj):
        if obj.user:
            return obj.user.email
        else:
            return obj.email

    user__email.short_description = _('E-mail')
    user__email.admin_order_field = 'user__email'

    def user__phone(self, obj):
        if obj.user:
            return obj.user.phone
        else:
            return obj.phone

    user__phone.short_description = _('Phone')
    user__phone.admin_order_field = 'user__phone'

    def project__name(self, obj):
        if obj.project:
            return obj.project.name
        else:
            return _('None')
    project__name.short_description = _('Project')
    project__name.admin_order_field = 'project__name'

    def project__organization__name(self, obj):
        if obj.project and obj.project.organization:
            return obj.project.organization.name
        else:
            return _('None')
    project__organization__name.short_description = _('Organization')
    project__organization__name.project__organization__name = 'project__organization__name'

    def project__address(self, obj):
        if obj.project:
            return obj.project.address
        else:
            return _('None')
    project__address.short_description = _('Address')
    project__address.admin_order_field = 'project__address'

    def get_queryset(self, request):
        qs = super(ApplyAdmin, self).get_queryset(request)
        return self.filter_by_country(request, qs, 'project__address')


admin_site.register(Apply, ApplyAdmin)
