from rest_framework import serializers
from ovp.apps.core import models
from ovp.apps.core.validators import skill_exist
from ovp.apps.channels.serializers import ChannelRelationshipSerializer


class SkillSerializer(ChannelRelationshipSerializer):
    class Meta:
        fields = ['id', 'name', 'slug']
        model = models.Skill


class SkillAssociationSerializer(ChannelRelationshipSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)

    class Meta:
        fields = ['id', 'name']
        model = models.Skill
        validators = [skill_exist]
