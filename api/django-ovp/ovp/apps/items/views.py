import json

from ovp.apps.items.models import Item, ItemImage, ItemDocument
from ovp.apps.items.serializers import ItemSerializer, ItemImageSerializer, ItemDocumentSerializer

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from rest_framework import decorators
from rest_framework import mixins
from rest_framework import response
from rest_framework import viewsets


@ChannelViewSet
class ItemViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    swagger_schema = None

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)


@ChannelViewSet
class ItemImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ItemImage.objects.all()
    serializer_class = ItemImageSerializer
    swagger_schema = None


@ChannelViewSet
class ItemDocumentViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ItemDocument.objects.all()
    serializer_class = ItemDocumentSerializer
    swagger_schema = None
