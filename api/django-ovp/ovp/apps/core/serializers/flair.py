from rest_framework import serializers
from ovp.apps.core import models
from ovp.apps.core.validators import cause_exist
from ovp.apps.uploads.serializers import UploadedImageSerializer
from ovp.apps.channels.serializers import ChannelRelationshipSerializer


class FlairSerializer(ChannelRelationshipSerializer):
    image = UploadedImageSerializer()

    class Meta:
        fields = ['id', 'name', 'value', 'image']
        model = models.Flair
