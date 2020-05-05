from ovp.apps.channels.serializers import ChannelRelationshipSerializer
from ovp.apps.projects import models
from ovp.apps.projects.validators import category_exist
from rest_framework import serializers


class CategoryRetrieveSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.Category
        fields = ['id', 'name', 'description', 'image', 'highlighted', 'slug']


class CategoryAssociationSerializer(ChannelRelationshipSerializer):

    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)

    class Meta:
        fields = ['id', 'name']
        model = models.Category
        validators = [category_exist]
