from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import response
from rest_framework import decorators
from rest_framework import response
from drf_yasg.utils import swagger_auto_schema

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from ovp.apps.projects import models
from ovp.apps.projects.serializers import category


@ChannelViewSet
class CategoryResourceViewSet(mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    """
    ProjectResourceViewSet resource endpoint
    """
    queryset = models.Category.objects.all()
    serializer_class = category.CategoryRetrieveSerializer

    def list(self, request):
        """ Retrieve a list of categories. """
        serializer = category.CategoryRetrieveSerializer(
            self.get_queryset(),
            many=True
        )
        return response.Response(serializer.data)

    def retrieve(self, *args, **kwargs):
        """ Retrieve a category by slug. """
        return super().retrieve(*args, **kwargs)
