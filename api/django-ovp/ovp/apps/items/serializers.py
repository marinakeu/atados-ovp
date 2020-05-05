from ovp.apps.items.models import Item, ItemImage, ItemDocument
from ovp.apps.uploads.serializers import UploadedImageSerializer, UploadedDocumentSerializer
from ovp.apps.channels.serializers import ChannelRelationshipSerializer

from rest_framework import serializers
from rest_framework.utils import model_meta


class ItemImageSerializer(ChannelRelationshipSerializer):
    image = UploadedImageSerializer(read_only=True)
    image_id = serializers.IntegerField(required=False)

    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'image_id', 'item']
        extra_kwargs = {'item': {'write_only': True}}


class ItemDocumentSerializer(ChannelRelationshipSerializer):
    document = UploadedDocumentSerializer(read_only=True)
    document_id = serializers.IntegerField(required=False)

    class Meta:
        model = ItemDocument
        fields = ['id', 'document', 'document_id', 'item']
        extra_kwargs = {'item': {'write_only': True}}


class ItemSerializer(ChannelRelationshipSerializer):
    images_data = serializers.SerializerMethodField()
    documents_data = serializers.SerializerMethodField()
    images = ItemImageSerializer(many=True, required=False)
    documents = ItemDocumentSerializer(many=True, required=False)

    class Meta:
        model = Item
        fields = [
            'id',
            'name',
            'about',
            'images',
            'images_data',
            'documents_data',
            'documents']

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        documents = validated_data.pop('documents', [])

        item = super(ItemSerializer, self).create(validated_data)

        # Images
        for image_data in images:
            image_data['item'] = item
            image_sr = ItemImageSerializer(
                data=image_data, context=self.context)
            image = image_sr.create(image_data)

        # Documents
        for document_data in documents:
            document_data['item'] = item
            document_sr = ItemDocumentSerializer(
                data=document_data, context=self.context)
            document = document_sr.create(document_data)

        return item

    def update(self, instance, validated_data):
        images = validated_data.pop('images', [])
        documents = validated_data.pop('documents', [])

        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Images

        items = ItemImage.objects.filter(item=instance, deleted=False)

        for image_data in images:
            if image_data['image_id'] not in [item.image_id for item in items]:
                image_data['item'] = instance
                image_sr = ItemImageSerializer(
                    data=image_data, context=self.context)
                image = image_sr.create(image_data)

            for item in items:
                if item.image_id not in [
                        image['image_id'] for image in images]:
                    item.delete()

        # Documents
        items = ItemDocument.objects.filter(item=instance, deleted=False)

        for document_data in documents:
            if document_data['document_id'] not in [
                    item.document_id for item in items]:
                document_data['item'] = instance
                document_sr = ItemDocumentSerializer(
                    data=document_data, context=self.context)
                document = document_sr.create(document_data)

        instance.save()

        return instance

    def get_images_data(self, item):
        queryset = ItemImage.objects.filter(item=item, deleted=False)
        serialized_data = ItemImageSerializer(
            queryset, many=True, context=self.context)
        return serialized_data.data

    def get_documents_data(self, item):
        queryset = ItemDocument.objects.filter(item=item, deleted=False)
        serialized_data = ItemDocumentSerializer(
            queryset, many=True, context=self.context)
        return serialized_data.data
