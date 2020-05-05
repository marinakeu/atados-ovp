import os

from django import forms
from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from martor.widgets import AdminMartorWidget

from ovp.apps.admin.resources import CleanModelResource
from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.channels.admin import TabularInline
from ovp.apps.projects.models import Project, VolunteerRole, Job, Work
from ovp.apps.uploads.models import UploadedDocument
from ovp.apps.organizations.models import Organization
from ovp.apps.core.models import GoogleAddress
from ovp.apps.core.models import SimpleAddress
from ovp.apps.organizations.admin import StateListFilter
from ovp.apps.organizations.admin import CityListFilter
from .job import JobInline
from .work import WorkInline

from ovp.apps.core.mixins import CountryFilterMixin

from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from jet.filters import RelatedFieldAjaxListFilter
from jet.filters import DateRangeFilter


class VolunteerRoleInline(TabularInline):
    model = VolunteerRole
    exclude = ['channel']


class DocumentInline(TabularInline):

    model = Project.documents.through
    exclude = ['channel']
    readonly_fields = ['download_link']
    verbose_name = "Document"
    verbose_name_plural = "Documents"

    def download_link(self, instance):
        url = instance.uploadeddocument.document.url
        return format_html('<a target="_blank" href="{}">Download</a>', url)


class GalleryInline(TabularInline):

    model = Project.galleries.through
    exclude = ['channel']
    verbose_name = "Gallery"
    verbose_name_plural = "Gallery"


class ProjectResource(CleanModelResource):

    id = Field(attribute='id', column_name='ID')
    name = Field(attribute='name', column_name='Nome do Projeto')
    description = Field(attribute='description', column_name='Descricao')
    causes = Field(column_name='Causas')
    organization_id = Field(column_name='ID ONG')
    organization = Field(column_name='ONG')
    address = Field(column_name='Endereço')
    city_state = Field(column_name='Cidade/Estado')
    neighborhood = Field(column_name='Bairro')
    link = Field(column_name='link')
    owner_id = Field(column_name='ID Responsavel')
    owner_name = Field(column_name='Nome Responsavel')
    owner_email = Field(column_name='Email Responsavel')
    owner_phone = Field(column_name='Telefone Responsavel')
    roles_count = Field(column_name='Número de funções')
    roles = Field(column_name='Funções')
    image = Field(column_name='Imagem')
    start_date = Field(column_name='Data de início')
    end_date = Field(column_name='Data de Encerramento')
    created_date = Field(column_name='Data de criação')
    closed_date = Field(column_name='Data de fechamento')
    benefited_people = Field(
        attribute='benefited_people',
        column_name='Pessoas beneficiadas'
    )
    applied_count = Field(
        attribute='applied_count',
        column_name='Número de inscritos'
    )
    disponibility = Field(column_name='Presencial ou a distancia')
    bookmark = Field(
        attribute='bookmark_count',
        column_name='Número de curtidas'
    )

    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'owner_id',
            'owner_name',
            'owner_email',
            'owner_phone',
            'organization_id',
            'organization',
            'address',
            'city_state',
            'neighborhood',
            'image',
            'description',
            'roles',
            'roles_count',
            'link',
            'disponibility',
            'causes',
            'start_date',
            'end_date',
            'applied_count',
            'benefited_people',
            'published',
            'closed',
            'bookmark',
            'created_date',
            'closed_date'
        )

    def before_export(self, qs, *args, **kwargs):
        qs = qs.prefetch_related('causes', 'job', 'work', 'roles')
        qs = qs.select_related('organization', 'address', 'owner', 'image')
        return qs.annotate(bookmark_count=Count('bookmarks'))

    def dehydrate_organization(self, project):
        if project.organization:
            return project.organization.name

    def dehydrate_organization_id(self, project):
        if project.organization:
            return project.organization.id

    def dehydrate_causes(self, project):
        if project.causes:
            return ", ".join([c.name for c in project.causes.all()])

    def dehydrate_owner_id(self, project):
        if project.owner:
            return project.owner.id

    def dehydrate_owner_name(self, project):
        if project.owner:
            return project.owner.name

    def dehydrate_owner_email(self, project):
        if project.owner:
            return project.owner.email

    def dehydrate_owner_phone(self, project):
        if project.owner:
            return project.owner.phone

    def dehydrate_image(self, project):
        api_url = os.environ.get('API_URL', None)
        try:
            if project.image:
                if api_url is not None:
                    return api_url + project.image.image_large.url
                else:
                    return project.image.image_large.url
        except ValueError:
            pass

    def dehydrate_created_date(self, project):
        if project.created_date:
            return project.created_date.strftime("%d/%m/%Y %H:%M:%S")
        return ""

    def dehydrate_closed_date(self, project):
        if project.closed_date:
            return project.closed_date.strftime("%d/%m/%Y %H:%M:%S")
        return ""

    def dehydrate_start_date(self, project):
        if hasattr(project, 'job'):
            if project.job.start_date:
                return project.job.start_date.strftime("%d/%m/%Y %H:%M:%S")
            return ""
        return "recorrente"

    def dehydrate_end_date(self, project):
        if hasattr(project, 'job'):
            if project.job.end_date:
                return project.job.end_date.strftime("%d/%m/%Y %H:%M:%S")
            return ""
        return "recorrente"

    def dehydrate_neighborhood(self, project):
        # TODO: FIX
        # This is generating one query per project on export
        # Maybe bring neighborhood into GoogleAddress as a field?
        if project.address is not None:
            if isinstance(project.address, GoogleAddress):
                qs = project.address.address_components.filter(
                    types__name="sublocality_level_1"
                )
                if qs.count():
                    return qs[0].long_name
                return ""
            if isinstance(project.address, SimpleAddress):
                return project.address.neighbourhood

    def dehydrate_address(self, project):
        if project.address is not None:
            if isinstance(project.address, GoogleAddress):
                return project.address.address_line
            if isinstance(project.address, SimpleAddress):
                return '{0}, {1} - {2} - {3}'.format(
                    project.address.street,
                    project.address.number,
                    project.address.neighbourhood,
                    project.address.city
                )

    def dehydrate_disponibility(self, project):
        obj = None
        if hasattr(project, 'job'):
            obj = project.job
        elif hasattr(project, 'work'):
            obj = project.work

        if obj:
            return "A distância" if obj.can_be_done_remotely else "Presencial"

        return None

    def dehydrate_link(self, project):
        site_url = os.environ.get('SITE_URL', None)
        if site_url:
            return site_url + project.slug
        return project.slug

    def dehydrate_city_state(self, project):
        if project.address is not None:
            if isinstance(project.address, GoogleAddress):
                return project.address.city_state
            if isinstance(project.address, SimpleAddress):
                return project.address.city

    def dehydrate_roles_count(self, project):
        return project.roles.count()

    def dehydrate_roles(self, project):
        roles = project.roles.all()
        if len(roles):
            return ", ".join([str(r.name) for r in roles])
        return ""


class BaseAux(ImportExportModelAdmin, ChannelModelAdmin, CountryFilterMixin):
    """
    Created to extends by ProjectAdmin
    """
    pass


class ProjectAdmin(BaseAux):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    fields = [
        ('id', 'highlighted'), ('name', 'slug'),
        ('organization', 'owner'),
        ('owner__name', 'owner__email', 'owner__phone'),

        ('applied_count', 'benefited_people'),
        ('volunteers__list'),
        ('can_be_done_remotely', 'skip_address_filter', 'chat_enabled'),

        ('published', 'closed', 'deleted', 'canceled'),
        ('published_date', 'closed_date', 'deleted_date', 'canceled_date'),

        'address',
        'image',
        'categories',
        'posts',
        'documents',
        'galleries',
        'flairs',

        ('created_date', 'modified_date'),

        'description', 'details',
        'skills', 'causes',
    ]

    resource_class = ProjectResource

    list_display = [
        'id',
        'created_date',
        'name',
        'highlighted',
        'published',
        'closed',
        'deleted',
        'organization__name',
        'city_state',
        'applied_count',
        'total_opportunities'
    ]

    list_filter = [
        ('closed_date', DateRangeFilter),
        ('canceled_date', DateRangeFilter),
        ('created_date', DateRangeFilter),  # fix: PONTUAL OU RECORRENTE
        'highlighted',
        'published',
        'closed',
        'deleted',
        StateListFilter,
        CityListFilter,
        'categories'
    ]

    list_editable = []

    search_fields = [
        'name', 'organization__name'
    ]

    readonly_fields = [
        'id',
        'created_date',
        'modified_date',
        'published_date',
        'closed_date',
        'deleted_date',
        'canceled_date',
        'applied_count',
        'max_applies_from_roles',
        'owner__name',
        'owner__email',
        'owner__phone',
        'can_be_done_remotely',
        'volunteers__list'
    ]

    raw_id_fields = []

    filter_horizontal = ('skills', 'causes',)

    inlines = [
        VolunteerRoleInline,
        DocumentInline,
        GalleryInline,
        JobInline, WorkInline
    ]

    def total_opportunities(self, obj):
        roles = obj.roles.all()
        if roles:
            return sum((role.vacancies or 0) + (role.applied_count or 0)
                       for role in roles)
        return 0
    total_opportunities.short_description = _('Opportunities')

    def can_be_done_remotely(self, obj):
        if obj.hasattr('job') and obj.job:
            return obj.job.can_be_done_remotely
        elif obj.hasattr('work') and obj.work:
            return obj.job.can_be_done_remotely
        else:
            return _('Type not specified')
    can_be_done_remotely.short_description = _('Can be done remotely?')

    def organization__name(self, obj):
        if obj.organization:
            return obj.organization.name
        else:
            return _('None')
    organization__name.short_description = _('Organization')
    organization__name.admin_order_field = 'organization__name'

    def owner__name(self, obj):
        return obj.owner and obj.owner.name or _('Owner not assigned')
    owner__name.short_description = _('Owner name')
    owner__name.admin_order_field = 'owner__name'

    def owner__email(self, obj):
        return obj.owner and obj.owner.email or _('Owner not assigned')
    owner__email.short_description = _('Owner email')
    owner__email.admin_order_field = 'owner__email'

    def owner__phone(self, obj):
        return obj.owner and obj.owner.phone or _('Owner not assigned')
    owner__phone.short_description = _('Owner phone')
    owner__phone.admin_order_field = 'owner__phone'

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        return self.filter_by_country(request, qs, 'address')

    def city_state(self, obj):
        if isinstance(obj.address, GoogleAddress):
            return obj.address.city_state
        else:
            return ""
    city_state.short_description = _("City/state")

    def volunteers__list(self, obj):
        site_url = os.environ.get('ADMIN_URL', None)
        if site_url:
            html_string = '<a href="{0}admin/projects/apply/?q={1}"' \
                ' target="__blank">Lista de Voluntários</a>'.format(
                    site_url,
                    obj.name,
                )
            return format_html(html_string)
        return ""


admin_site.register(Project, ProjectAdmin)
