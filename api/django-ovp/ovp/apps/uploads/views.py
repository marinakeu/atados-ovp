import json

from ovp.apps.uploads.models import UploadedImage, UploadedDocument
from ovp.apps.uploads.serializers import (
    UploadedImageSerializer, UploadedDocumentSerializer
)

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .helpers import perform_image_crop


image_param = openapi.Parameter(
    'image',
    openapi.IN_FORM,
    description="image file",
    type=openapi.TYPE_FILE
)


@ChannelViewSet
class UploadedImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = UploadedImage.objects.all()

    @swagger_auto_schema(manual_parameters=[image_param],
                         responses={201: UploadedImageSerializer})
    def create(self, request, *args, **kwargs):
        """ Upload image. """
        upload_data = {}

        if request.data.get('image', None):
            upload_data['image'] = request.data.get('image')

        upload_header = request.META.get('HTTP_X_UNAUTHENTICATED_UPLOAD', None)
        is_authenticated = request.user.is_authenticated

        if request.data.get('crop_rect', None):
            crop_rect = request.data.get('crop_rect')
            if isinstance(crop_rect, str):
                crop_rect = json.loads(crop_rect)
            upload_data['image'] = perform_image_crop(
                upload_data['image'],
                crop_rect
            )
            request.FILES['image'] = upload_data['image']

        if is_authenticated or upload_header:
            if upload_header:
                upload_data['user'] = None

            if is_authenticated:
                upload_data['user'] = request.user.id

            serializer = UploadedImageSerializer(
                data=upload_data,
                context=self.get_serializer_context()
            )

            if serializer.is_valid():
                self.object = serializer.save()
                headers = self.get_success_headers(serializer.data)
                return response.Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )

            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response(status=status.HTTP_401_UNAUTHORIZED)


@ChannelViewSet
class UploadedDocumentViewSet(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    queryset = UploadedDocument.objects.all()
    serializer_class = UploadedDocumentSerializer
    swagger_schema = None

    def create(self, request, *args, **kwargs):
        upload_data = {}

        if request.data.get('document', None):
            upload_data['document'] = request.data.get('document')

        upload_header = request.META.get('HTTP_X_UNAUTHENTICATED_UPLOAD', None)
        is_authenticated = request.user.is_authenticated

        if is_authenticated or upload_header:
            if upload_header:
                upload_data['user'] = None

            if is_authenticated:
                upload_data['user'] = request.user.id

            serializer = self.get_serializer(
                data=upload_data,
                context=self.get_serializer_context()
            )

            if serializer.is_valid():
                self.object = serializer.save()
                headers = self.get_success_headers(serializer.data)
                return response.Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )

            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response(status=status.HTTP_401_UNAUTHORIZED)
