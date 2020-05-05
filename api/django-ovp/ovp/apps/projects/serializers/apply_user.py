from ovp.apps.projects import models
from rest_framework import serializers

from ovp.apps.channels.serializers import ChannelRelationshipSerializer
from ovp.apps.core.helpers import get_address_serializers
from ovp.apps.uploads.serializers import UploadedImageSerializer
from ovp.apps.organizations.serializers import OrganizationSearchSerializer
from ovp.apps.projects.serializers.disponibility import (
    DisponibilitySerializer,
    add_disponibility_representation
)

from ovp.apps.projects.serializers import role

#  Address serializers
address_serializers = get_address_serializers()


######################
# Serializers
######################


class ProjectApplyRetrieveSerializer(ChannelRelationshipSerializer):

    image = UploadedImageSerializer()
    address = address_serializers[1]()
    organization = OrganizationSearchSerializer()
    disponibility = DisponibilitySerializer(many=True, required=False)

    class Meta:
        model = models.Project
        fields = [
            'slug',
            'image',
            'name',
            'description',
            'highlighted',
            'published_date',
            'address',
            'details',
            'created_date',
            'organization',
            'minimum_age',
            'applied_count',
            'max_applies',
            'max_applies_from_roles',
            'closed',
            'closed_date',
            'published',
            'hidden_address',
            'crowdfunding',
            'public_project',
            'disponibility',
            'rating'
        ]

    @add_disponibility_representation
    def to_representation(self, instance):
        return super().to_representation(instance)


class ApplyUserRetrieveSerializer(ChannelRelationshipSerializer):
    project = ProjectApplyRetrieveSerializer()
    role = role.VolunteerRoleApplySerializer()

    class Meta:
        model = models.Apply
        fields = ['id', 'date', 'canceled_date', 'project', 'role', 'status']
