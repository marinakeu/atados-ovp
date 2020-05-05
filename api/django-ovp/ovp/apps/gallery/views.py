from django.utils import timezone

from ovp.apps.channels.viewsets.decorators import ChannelViewSet
from ovp.apps.gallery.serializers import (GalleryRetrieveSerializer,
                                          GalleryCreateUpdateSerializer)
from ovp.apps.gallery.models import Gallery
from ovp.apps.gallery.permissions import GalleryEditAllowed

from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import response
from rest_framework import status


@ChannelViewSet
class GalleryResourceViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):

    lookup_field = "uuid"

    def get_queryset(self, *args, **kwargs):
        return Gallery.objects.filter(deleted=False)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "retrieve":
            return GalleryRetrieveSerializer
        if self.action == "create":
            return GalleryCreateUpdateSerializer
        if self.action == 'partial_update':
            return GalleryCreateUpdateSerializer

        return GalleryRetrieveSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (permissions.IsAuthenticated,)
        if self.action == 'partial_update':
            self.permission_classes = (
                permissions.IsAuthenticated,
                GalleryEditAllowed
            )
        if self.action == 'retrieve':
            self.permission_classes = ()
        if self.action == 'delete':
            self.permission_classes = (
                permissions.IsAuthenticated,
                GalleryEditAllowed
            )
        return super().get_permissions()

    def partial_update(self, request, *args, **kwargs):
        """ Partially update an gallery object. """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # pragma: no cover
        if getattr(instance, '_prefetched_objects_cache', None):
            instance = self.get_object()
            serializer = self.get_serializer(instance)

        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """ Create a gallery. """
        owner_in_data = request.data.get('owner', None)
        request.data['owner'] = owner_in_data or request.user.pk

        serializer = self.get_serializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def delete(self, request, *args, **kwargs):
        """ Delete a gallery. """
        instance = self.get_object()
        instance.deleted = True
        instance.deleted_date = timezone.now()
        instance.save()

        return response.Response({"deleted": True}, status=200)
