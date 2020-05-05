# Helper user view to test decorator restricts queryset
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import response

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from ovp.apps.users.models import User
from ovp.apps.users.serializers import UserCreateSerializer

from ovp.apps.projects.models.project import Project
from ovp.apps.projects.serializers.project import ProjectCreateUpdateSerializer


class BaseHelperMixin(mixins.CreateModelMixin,
                      mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    base to be extended in the test helpers
    """
    pass


@ChannelViewSet
class ChannelUserTestViewSet(BaseHelperMixin):
    serializer_class = UserCreateSerializer

    def get_queryset(self):
        return User.objects.all().order_by("pk")


@ChannelViewSet
class ChannelProjectTestViewSet(BaseHelperMixin):
    serializer_class = ProjectCreateUpdateSerializer

    def get_queryset(self):
        return Project.objects.all().order_by("pk")


@ChannelViewSet
class OverrideQuerysetTestViewSet(mixins.CreateModelMixin,
                                  viewsets.GenericViewSet):
    queryset = Project.objects.all().order_by("pk")
    serializer_class = ProjectCreateUpdateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
