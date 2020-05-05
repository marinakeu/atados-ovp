from django.conf.urls import url, include
from rest_framework import routers
from ovp.apps.search import views


project_search = routers.SimpleRouter()
project_search.register(
    r'projects',
    views.ProjectSearchResource,
    'search-projects')
project_search.register(
    r'projects/map-data',
    views.ProjectMapDataResource,
    'search-projects-map-data')

organization_search = routers.SimpleRouter()
organization_search.register(
    r'organizations',
    views.OrganizationSearchResource,
    'search-organizations')
project_search.register(
    r'organizations/map-data',
    views.OrganizationMapDataResource,
    'search-organizations-map-data')

user_search = routers.SimpleRouter()
user_search.register(r'users', views.UserSearchResource, 'search-users')

urlpatterns = [
    url(
        r'^search/',
        include(project_search.urls)
    ),
    url(
        r'^search/',
        include(organization_search.urls)
    ),
    url(
        r'^search/',
        include(user_search.urls)
    ),
    url(
        r'^search/all/',
        views.SearchAllResource.as_view(),
        name='search-all'
    ),
    url(
        r'^search/available-cities/(?P<country>[^/]+)/',
        views.CountryCities.as_view(),
        name='available-country-cities'
    ),
]
