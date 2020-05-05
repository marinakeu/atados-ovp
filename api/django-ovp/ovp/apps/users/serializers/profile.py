from ovp.apps.users.models.profile import get_profile_model
from ovp.apps.users.models.profile import gender_choices
from ovp.apps.users.helpers import get_settings, import_from_string

from ovp.apps.core.models import Skill
from ovp.apps.core.models import Cause
from ovp.apps.core.models.address import GoogleAddress
from ovp.apps.core.serializers.skill import (
    SkillSerializer, SkillAssociationSerializer
)
from ovp.apps.core.serializers.cause import (
    CauseSerializer, CauseAssociationSerializer
)
from ovp.apps.core.serializers import GoogleAddressSerializer

from ovp.apps.channels.serializers import ChannelRelationshipSerializer

from rest_framework import serializers


class ProfileCreateUpdateSerializer(ChannelRelationshipSerializer):
    # we do not allow the user to create skills, only associate with
    # existing skills, so we do it manually on .create method
    skills = SkillAssociationSerializer(many=True, required=False)
    causes = CauseAssociationSerializer(many=True, required=False)
    address = GoogleAddressSerializer(required=False)

    class Meta:
        model = get_profile_model()
        fields = [
            'full_name',
            'about',
            'skills',
            'causes',
            'gender',
            'address',
            'hidden_address',
            'birthday_date',
            'department',
            'has_done_volunteer_work_before'
        ]

    def create(self, validated_data):
        skills = validated_data.pop('skills', [])
        causes = validated_data.pop('causes', [])
        address_data = validated_data.pop('address', None)

        # Address
        if address_data:
            address_sr = GoogleAddressSerializer(
                data=address_data, context=self.context
            )
            address = address_sr.create(address_data)
            validated_data['address'] = address

        # Create profile
        profile = super().create(validated_data)

        # Associate skills
        for skill in skills:
            s = Skill.objects.get(pk=skill['id'])
            profile.skills.add(s)

        # Associate causes
        for cause in causes:
            c = Cause.objects.get(pk=cause['id'])
            profile.causes.add(c)

        return profile

    def update(self, instance, validated_data):
        skills = validated_data.pop('skills', None)
        causes = validated_data.pop('causes', None)
        address_data = validated_data.pop('address', None)

        # Associate skills
        if skills:
            instance.skills.clear()
            for skill in skills:
                s = Skill.objects.get(pk=skill['id'])
                instance.skills.add(s)

        # Associate causes
        if causes:
            instance.causes.clear()
            for cause in causes:
                c = Cause.objects.get(pk=cause['id'])
                instance.causes.add(c)

        # Address
        if address_data:
            address_sr = GoogleAddress(
                typed_address=address_data['typed_address'],
                typed_address2=address_data.get(
                    'typed_address2',
                    None))
            address_sr.save(object_channel=instance.channel.slug)
            validated_data['address'] = address_sr

        return super().update(instance, validated_data)


class ProfileRetrieveSerializer(ChannelRelationshipSerializer):
    skills = SkillSerializer(many=True)
    causes = CauseSerializer(many=True)
    gender = serializers.ChoiceField(choices=gender_choices)
    address = GoogleAddressSerializer(required=False)

    class Meta:
        model = get_profile_model()
        fields = [
            'full_name',
            'about',
            'skills',
            'causes',
            'gender',
            'address',
            'hidden_address',
            'birthday_date',
            'has_done_volunteer_work_before'
        ]


class ProfileSearchSerializer(ChannelRelationshipSerializer):
    skills = SkillSerializer(many=True)
    causes = CauseSerializer(many=True)
    gender = serializers.ChoiceField(choices=gender_choices)

    class Meta:
        model = get_profile_model()
        fields = ['full_name', 'skills', 'causes', 'gender']


def get_profile_serializers():
    s = get_settings()
    serializers = s.get('PROFILE_SERIALIZER_TUPLE', None)
    if isinstance(serializers, tuple):
        return [import_from_string(s) for s in serializers]
    return (
        ProfileCreateUpdateSerializer,
        ProfileRetrieveSerializer,
        ProfileSearchSerializer)
