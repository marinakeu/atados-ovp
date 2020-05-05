from rest_framework import serializers

from ovp.apps.channels.models import Channel


class ChannelRelationshipSerializer(serializers.ModelSerializer):
    """
    This serializer is required for models that extend ChannelRelationship.
    It automatically passes request channel down to the model.
    """

    def create(self, validated_data):
        # Force exception if request is unavailable
        request = self.context["request"]
        validated_data["object_channel"] = request.channel
        return super().create(validated_data)


class ChannelRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ["name", "slug"]
