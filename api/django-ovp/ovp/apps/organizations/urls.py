from django.conf.urls import url, include
from rest_framework import routers

from ovp.apps.organizations import views


router = routers.DefaultRouter()
router.register(
    r'organizations',
    views.OrganizationResourceViewSet,
    'organization'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
