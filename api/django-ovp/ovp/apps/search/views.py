import json
from django.core.exceptions import PermissionDenied

from ovp.apps.core.pagination import NoPagination

from ovp.apps.projects.serializers.project import ProjectSearchSerializer
from ovp.apps.projects.serializers.project import (
    ProjectMapDataSearchRetrieveSerializer
)
from ovp.apps.projects.models import Project

from ovp.apps.organizations.models import Organization
from ovp.apps.organizations.serializers import OrganizationSearchSerializer
from ovp.apps.organizations.serializers import (
    OrganizationMapDataSearchRetrieveSerializer
)

from ovp.apps.users.models.user import User
from ovp.apps.users.serializers.user import get_user_search_serializer
from ovp.apps.users.models.profile import get_profile_model, UserProfile

from ovp.apps.search import helpers
from ovp.apps.search import filters
from ovp.apps.search import querysets
from ovp.apps.search.decorators import cached

from ovp.apps.channels.cache import get_channel_setting

from django.core.cache import cache
from django.conf import settings

from rest_framework.reverse import reverse
from rest_framework import viewsets
from rest_framework import views
from rest_framework import mixins
from rest_framework import response
from rest_framework import decorators
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db.models import Q
from haystack.query import SearchQuerySet, SQ


organization_params = [
    openapi.Parameter(
        'query',
        openapi.IN_QUERY,
        description="Query string.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'cause',
        openapi.IN_QUERY,
        description="List of causes(OR filter applied). Must be a string "
        "formatted as array. Eg: '[1, 3, 7]'",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'address',
        openapi.IN_QUERY,
        description="Filter by address.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'name',
        openapi.IN_QUERY,
        description="Search by name.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'highlighted',
        openapi.IN_QUERY,
        description="Wether project is highlighted or not. Must be a string, "
        "either 'false', 'true' or 'both'.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'published',
        openapi.IN_QUERY,
        description="Wether project is published or not. Must be a string, "
        "either 'false', 'true' or 'both'.",
        type=openapi.TYPE_STRING),
]


class OrganizationSearchResource(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = (
        'slug',
        'name',
        'website',
        'facebook_page',
        'details',
        'description',
        'type',
        'hidden_address')
    serializer_class = OrganizationSearchSerializer

    @swagger_auto_schema(manual_parameters=organization_params)
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    def get_cache_key(self):
        if self.request.user.is_anonymous:
            return 'organizations-{}-{}'.format(
                self.request.channel, hash(
                    frozenset(
                        self.request.GET.items())))
        return None

    @cached
    def get_queryset(self):
        params = self.request.GET

        highlighted = params.get('highlighted') == 'true'
        published = params.get('published', 'true')

        query = params.get('query', None)
        cause = params.get('cause', None)
        address = params.get('address', None)
        name = params.get('name', None)
        category = params.get('category', None)

        queryset = SearchQuerySet().models(Organization)
        queryset = queryset.filter(highlighted=1) if highlighted else queryset
        # Added 'startswith' filter (django haystack version 2.8.1).
        queryset = queryset.filter(content__startswith=query) if query else queryset
        queryset = filters.by_name(queryset, name) if name else queryset
        queryset = filters.by_published(queryset, published)
        queryset = filters.by_address(
            queryset, address) if address else queryset
        queryset = filters.by_causes(queryset, cause) if cause else queryset
        queryset = filters.by_categories(queryset, category) if category else queryset
        queryset = filters.by_channel_content_flow(
            queryset, self.request.channel)

        result_keys = [q.pk for q in queryset]
        result = querysets.get_organization_queryset(
            request=self.request).filter(
            pk__in=result_keys)
        result = filters.filter_out(
            result,
            "FILTER_OUT_ORGANIZATIONS",
            self.request.channel)

        return result


class OrganizationMapDataResource(OrganizationSearchResource):
    pagination_class = NoPagination
    serializer_class = OrganizationMapDataSearchRetrieveSerializer
    swagger_schema = None


project_params = [
    openapi.Parameter(
        'query',
        openapi.IN_QUERY,
        description="Query string.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'cause',
        openapi.IN_QUERY,
        description="List of causes(OR filter applied). Must be a string "
        "formatted as array. Eg: '[1, 3, 7]'",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'skill',
        openapi.IN_QUERY,
        description="List of skills(OR filter applied). Must be a string "
        "formatted as array. Eg: '[1, 3, 7]'",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'category',
        openapi.IN_QUERY,
        description="List of categories(OR filter applied). Must be a string "
        "formatted as array. Eg: '[1, 2, 3]'",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'address',
        openapi.IN_QUERY,
        description="Filter by address.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'name',
        openapi.IN_QUERY,
        description="Search by name.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'highlighted',
        openapi.IN_QUERY,
        description="Wether project is highlighted or not. Must be a string, "
        "either 'false', 'true' or 'both'.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'published',
        openapi.IN_QUERY,
        description="Wether project is published or not. Must be a string, "
        "either 'false', 'true' or 'both'.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'closed',
        openapi.IN_QUERY,
        description="Wether project is closed or not. Must be a string, "
        "either 'false', 'true' or 'both'.",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'organization',
        openapi.IN_QUERY,
        description="List of organization ids to search in(OR filter applied)."
        " Must be a string formatted as array. Eg: '[1, 3, 7]",
        type=openapi.TYPE_STRING),
    openapi.Parameter(
        'disponibility',
        openapi.IN_QUERY,
        description="List of disponibility types(OR filter applied). Available"
        " types are 'work', 'job' and 'remotely'. Must be a string formatted "
        "as array. Eg: '['job', 'remotely']",
        type=openapi.TYPE_STRING),
]


class ProjectSearchResource(mixins.ListModelMixin, viewsets.GenericViewSet):
    filter_backends = (filters.ProjectRelevanceOrderingFilter,)
    ordering_fields = (
        'name',
        'slug',
        'details',
        'description',
        'highlighted',
        'published_date',
        'created_date',
        'max_applies',
        'minimum_age',
        'hidden_address',
        'crowdfunding',
        'public_project',
        'relevance',
        'closed',
        'published',
        'job__end_date'
    )
    serializer_class = ProjectSearchSerializer

    @swagger_auto_schema(manual_parameters=project_params)
    def list(self, *args, **kwargs):
        return super(ProjectSearchResource, self).list(*args, **kwargs)

    def get_cache_key(self):
        if self.request.user.is_anonymous:
            return 'projects-{}-{}'.format(
                self.request.channel,
                hash(frozenset(self.request.GET.items()))
            )
        return None

    @cached
    def get_queryset(self):
        params = self.request.GET

        query = params.get('query', None)
        cause = params.get('cause', None)
        skill = params.get('skill', None)
        category = params.get('category', None)
        address = params.get('address', None)
        highlighted = (params.get('highlighted') == 'true')
        name = params.get('name', None)
        published = params.get('published', 'true')
        closed = params.get('closed', 'false')
        organization = params.get('organization', None)
        disponibility = params.get('disponibility', None)
        date = params.get('date', None)
        manageable = params.get('manageable', None)

        queryset = SearchQuerySet().models(Project)
        queryset = queryset.filter(highlighted=1) if highlighted else queryset
        # Added 'startswith' filter (django haystack version 2.8.1).
        queryset = queryset.filter(content__startswith=query) if query else queryset
        queryset = filters.by_published(queryset, published)
        queryset = filters.by_closed(queryset, closed)
        queryset = filters.by_address(queryset, address, project=True)
        queryset = filters.by_name(queryset, name)
        queryset = filters.by_skills(queryset, skill)
        queryset = filters.by_causes(queryset, cause)
        queryset = filters.by_categories(queryset, category)
        queryset = filters.by_disponibility(queryset, disponibility)
        queryset = filters.by_date(queryset, date)
        # queryset = filters.by_organizations(queryset, organization)
        queryset = filters.by_channel_content_flow(
            queryset, self.request.channel)

        result_keys = [q.pk for q in queryset]

        result = querysets.get_project_queryset(
            request=self.request).filter(
            pk__in=result_keys)

        if manageable == 'true' and self.request.user.is_authenticated:
            result = result.filter(
                Q(organization__members=self.request.user) |
                Q(organization__owner=self.request.user) |
                Q(owner=self.request.user)
            )

        if organization:
            org = [o for o in organization.split(',')]
            result = result.filter(organization__in=org)

        result = filters.filter_out(
            result,
            "FILTER_OUT_PROJECTS",
            self.request.channel)

        return result


class ProjectMapDataResource(ProjectSearchResource):
    pagination_class = NoPagination
    serializer_class = ProjectMapDataSearchRetrieveSerializer
    swagger_schema = None


class SearchAllResource(views.APIView):

    def get(self, request):
        """ Retrieve list of available projects and organizations. """
        resp = self.get_object_lists()
        return response.Response(resp)

    @cached
    def get_object_lists(self):
        result = {"projects": [], "organizations": []}

        project_view = ProjectSearchResource.as_view({'get': 'list'})
        projects = project_view(self.request._request)

        organization_view = OrganizationSearchResource.as_view({'get': 'list'})
        organizations = organization_view(self.request._request)

        result["projects"] = projects.data
        result["organizations"] = organizations.data
        return result

    def get_cache_key(self):
        if self.request.user.is_anonymous:
            return 'organizations-projects-{}-{}'.format(
                self.request.channel,
                hash(frozenset(self.request.GET.items()))
            )
        return None


class UserSearchResource(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = get_user_search_serializer()
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('slug', 'name')

    @swagger_auto_schema(auto_schema=None)
    def list(self, *args, **kwargs):
        return super(UserSearchResource, self).list(*args, **kwargs)

    def initialize_request(self, *args, **kwargs):
        request = super(
            UserSearchResource,
            self).initialize_request(
            *
            args,
            **kwargs)
        self.check_user_search_enabled(request.channel)
        return request

    def check_user_search_enabled(self, channel):
        if int(get_channel_setting(channel, "ENABLE_USER_SEARCH")[0]) == 0:
            raise PermissionDenied

    def get_cache_key(self):
        return 'users-{}-{}'.format(self.request.channel,
                                    hash(frozenset(self.request.GET.items())))

    @cached
    def get_queryset(self):
        params = self.request.GET

        cause = params.get('cause', None)
        skill = params.get('skill', None)
        name = params.get('name', None)

        queryset = SearchQuerySet().models(User)
        queryset = filters.by_skills(queryset, skill)
        queryset = filters.by_causes(queryset, cause)
        queryset = filters.by_name(queryset, name)
        queryset = queryset.filter(channel=self.request.channel)

        result_keys = [q.pk for q in queryset]
        related_field_name = get_profile_model()._meta.get_field('user')
        related_field_name = related_field_name.related_query_name()

        result = User.objects.order_by('-pk').filter(
            is_active=True,
            pk__in=result_keys,
            public=True).prefetch_related(
            related_field_name +
            '__skills',
            related_field_name +
            '__causes').select_related(related_field_name)

        return result


class CountryCities(views.APIView):
    def get(self, request, country):
        """ Retrieve list of available cities for country. """
        self.country = country
        result = self.get_country_cities(country)
        return response.Response(result)

    @cached
    def get_country_cities(self, country):
        result = {"projects": [], "organizations": [], "common": []}

        search_term = helpers.whoosh_raw("{}-country".format(country))

        queryset = SearchQuerySet().models(Project).filter(
            address_components__exact=search_term,
            published=1,
            closed=0,
            channel=self.request.channel)
        projects = helpers.get_cities(queryset)

        queryset = SearchQuerySet().models(Organization).filter(
            address_components__exact=search_term,
            published=1,
            channel=self.request.channel
        )
        organizations = helpers.get_cities(queryset)

        common = projects & organizations
        projects = projects - common
        organizations = organizations - common

        result["common"] = sorted(common)
        result["projects"] = sorted(projects)
        result["organizations"] = sorted(organizations)

        return result

    def get_cache_key(self):
        return "available-cities-{}-{}".format(
            self.request.channel, hash(self.country))
