from rest_framework import routers

from django.conf.urls import url, include

from ovp.apps.channels.tests.helpers import views

test_user_resource = routers.SimpleRouter()
test_user_resource.register(
    r"test-users",
    views.ChannelUserTestViewSet,
    "test-users"
)

test_project_resource = routers.SimpleRouter()
test_project_resource.register(
    r"test-projects",
    views.ChannelProjectTestViewSet,
    "test-projects"
)

urlpatterns = [
    url(r"^", include(test_user_resource.urls)),
    url(r"^", include(test_project_resource.urls)),
]
