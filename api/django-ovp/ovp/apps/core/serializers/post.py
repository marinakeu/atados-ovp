from rest_framework import serializers
from ovp.apps.core import models
from ovp.apps.channels.serializers import ChannelRelationshipSerializer

from ovp.apps.gallery.serializers import (
    GalleryAssociationSerializer,
    GalleryRetrieveSerializer
)


class PostRetrieveSerializer(ChannelRelationshipSerializer):
    gallery = GalleryRetrieveSerializer()

    class Meta:
        model = models.Post
        fields = [
            'id',
            'title',
            'content',
            'reply_to',
            'gallery',
            'published',
            'created_date',
            'modified_date'
        ]


class PostCreateSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.Post
        fields = ['content', 'title', 'reply_to', 'user', 'gallery']


class PostUpdateSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.Post
        fields = ['title', 'content', 'gallery']
