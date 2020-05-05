from ovp.apps.uploads import helpers
from ovp.apps.uploads.models import UploadedImage, UploadedDocument

from ovp.apps.channels.serializers import ChannelRelationshipSerializer

from rest_framework import serializers


class UploadedImageSerializer(ChannelRelationshipSerializer):
    image_url = serializers.SerializerMethodField()
    image_small_url = serializers.SerializerMethodField()
    image_medium_url = serializers.SerializerMethodField()
    image_large_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedImage
        fields = (
            'id',
            'user',
            'image',
            'image_url',
            'image_small_url',
            'image_medium_url',
            'image_large_url'
        )
        read_only_fields = ('image_small', 'image_medium', 'image_large')
        extra_kwargs = {
            'image': {'write_only': True},
            'crop_rect': {'write_only': True}
        }

    def get_image_url(self, obj):
        if obj.absolute:
            return obj.image.name if obj.image else ""
        absolute_uri = helpers.build_absolute_uri(
            self.context['request'],
            obj.image
        )
        return absolute_uri if obj.image else ""

    def get_image_small_url(self, obj):
        if obj.absolute:
            return obj.image_small.name if obj.image_small else ""
        absolute_uri = helpers.build_absolute_uri(
            self.context['request'],
            obj.image_small
        )
        return absolute_uri if obj.image_small else ""

    def get_image_medium_url(self, obj):
        if obj.absolute:
            return obj.image_medium.name if obj.image_medium else ""
        absolute_uri = helpers.build_absolute_uri(
            self.context['request'],
            obj.image_medium
        )
        return absolute_uri if obj.image_medium else ""

    def get_image_large_url(self, obj):
        if obj.absolute:
            return obj.image_large.name if obj.image_large else ""
        absolute_uri = helpers.build_absolute_uri(
            self.context['request'],
            obj.image_large
        )
        return absolute_uri if obj.image_large else ""


class UploadedImageAssociationSerializer(ChannelRelationshipSerializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ['id', 'image_small', 'image_medium', 'image_large']
        read_only_fields = ('image_small', 'image_medium', 'image_large')
        model = UploadedImage


class ImageGallerySerializer(UploadedImageSerializer):
    name = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)

    class Meta:
        model = UploadedImage
        read_only_fields = ('image_small', 'image_medium', 'image_large')
        fields = (
            'id',
            'image_url',
            'image_small_url',
            'image_medium_url',
            'image_large_url',
            'name',
            'category'
        )


class UploadedDocumentSerializer(ChannelRelationshipSerializer):
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedDocument
        fields = ('id', 'user', 'document', 'document_url')
        extra_kwargs = {'document': {'write_only': True}}

    def get_document_url(self, obj):
        absolute_uri = helpers.build_absolute_uri(
            self.context['request'],
            obj.document
        )
        return absolute_uri if obj.document else ""


class UploadedDocumentAssociationSerializer(ChannelRelationshipSerializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ('id', 'document')
        read_only_fields = ('document', )
        model = UploadedDocument
