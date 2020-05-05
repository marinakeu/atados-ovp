from django.core.exceptions import ValidationError

from ovp.apps.uploads.serializers import UploadedImageSerializer

from ovp.apps.users.models.user import User

from ovp.apps.core.models import Cause
from ovp.apps.core.helpers import get_address_serializers
from ovp.apps.core.serializers.cause import (
    CauseSerializer, CauseAssociationSerializer
)
from ovp.apps.core.serializers.flair import FlairSerializer

from ovp.apps.organizations import models
from ovp.apps.organizations import validators
from ovp.apps.organizations.decorators import hide_address

from ovp.apps.projects.models import Project

from ovp.apps.channels.serializers import (
    ChannelRelationshipSerializer, ChannelRetrieveSerializer
)

from ovp.apps.gallery.models import Gallery
from ovp.apps.gallery.serializers import (GalleryAssociationSerializer,
                                          GalleryRetrieveSerializer)

from rest_framework import serializers
from rest_framework import permissions
from rest_framework import fields
from rest_framework.utils import model_meta

""" Address serializers """
address_serializers = get_address_serializers()


""" Serializers """


class OrganizationCreateSerializer(ChannelRelationshipSerializer):
    address = address_serializers[0](required=False)
    causes = CauseAssociationSerializer(many=True, required=False)
    image = UploadedImageSerializer(required=False)
    image_id = serializers.IntegerField(required=False)
    cover = UploadedImageSerializer(required=False)
    cover_id = serializers.IntegerField(required=False)
    galleries = GalleryAssociationSerializer(many=True, required=False)

    class Meta:
        model = models.Organization
        fields = [
            'id',
            'slug',
            'owner',
            'document',
            'name',
            'website',
            'facebook_page',
            'instagram_user',
            'address',
            'details',
            'description',
            'type',
            'image',
            'image_id',
            'cover',
            'cover_id',
            'hidden_address',
            'causes',
            'contact_name',
            'contact_email',
            'contact_phone',
            'benefited_people',
            'galleries',
            'allow_donations']

    def create(self, validated_data):
        causes = validated_data.pop('causes', [])
        galleries = validated_data.pop('galleries', [])
        address_data = validated_data.pop('address', None)

        # Address
        if address_data:
            address_sr = address_serializers[0](
                data=address_data, context=self.context)
            address = address_sr.create(address_data)
            validated_data['address'] = address

        # Organization
        organization = super(
            OrganizationCreateSerializer,
            self).create(validated_data)

        # Associate causes
        for cause in causes:
            c = Cause.objects.get(pk=cause['id'])
            organization.causes.add(c)

        # Associate galleries
        for gallery in galleries:
            c = Gallery.objects.get(pk=gallery['id'])
            organization.galleries.add(c)

        return organization

    def update(self, instance, validated_data):
        causes = validated_data.pop('causes', [])
        galleries = validated_data.pop('galleries', [])
        address_data = validated_data.pop('address', None)

        # Iterate and save fields as drf default
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)

        # Save related resources
        if address_data:
            address_sr = address_serializers[0](
                data=address_data, context=self.context)
            address = address_sr.create(address_data)
            instance.address = address

        # Associate causes
        if causes:
            instance.causes.remove(
                *
                Cause.objects.filter(
                    channel__slug=self.context["request"].channel))
            for cause in causes:
                c = Cause.objects.get(pk=cause['id'])
                instance.causes.add(c)

        # Associate galleries
        if galleries:
            instance.galleries.remove(
                *
                Gallery.objects.filter(
                    channel__slug=self.context["request"].channel))
            for gallery in galleries:
                g = Gallery.objects.get(pk=gallery['id'])
                instance.galleries.add(g)

        instance.save()

        return instance


class UserOrganizationRetrieveSerializer(ChannelRelationshipSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone']


class MemberRetrieveSerializer(ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()

    class Meta:
        model = User
        fields = ['uuid', 'name', 'avatar', 'slug']


class DonatorRetrieveSerializer(MemberRetrieveSerializer):
    pass


class OrganizationSearchSerializer(ChannelRelationshipSerializer):
    address = address_serializers[1]()
    image = UploadedImageSerializer()
    is_bookmarked = serializers.BooleanField()
    channel = ChannelRetrieveSerializer()

    class Meta:
        model = models.Organization
        fields = [
            'id',
            'slug',
            'owner',
            'name',
            'website',
            'facebook_page',
            'instagram_user',
            'address',
            'details',
            'description',
            'type',
            'image',
            'is_bookmarked',
            'verified',
            'rating',
            'channel']


class OrganizationRetrieveSerializer(ChannelRelationshipSerializer):
    address = address_serializers[1]()
    image = UploadedImageSerializer()
    cover = UploadedImageSerializer()
    causes = CauseSerializer(many=True)
    flairs = FlairSerializer(many=True)
    owner = UserOrganizationRetrieveSerializer()
    members = MemberRetrieveSerializer(many=True)
    galleries = GalleryRetrieveSerializer(many=True)
    is_bookmarked = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    donators = DonatorRetrieveSerializer(many=True)
    channel = ChannelRetrieveSerializer()

    class Meta:
        model = models.Organization
        fields = [
            'id',
            'slug',
            'owner',
            'document',
            'name',
            'website',
            'facebook_page',
            'instagram_user',
            'address',
            'details',
            'description',
            'type',
            'image',
            'cover',
            'published',
            'hidden_address',
            'causes',
            'galleries',
            'flairs',
            'members',
            'contact_name',
            'contact_phone',
            'contact_email',
            'is_bookmarked',
            'verified',
            'projects_count',
            'rating',
            'benefited_people',
            'channel',
            'allow_donations',
            'donators']

    def get_is_bookmarked(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            return instance.is_bookmarked(user)
        return False

    def get_projects_count(self, instance):
        total = 0
        try:
            total = Project.objects.filter(
                organization=instance, published=True).count()
        except BaseException:
            pass

        return total

    @hide_address
    def to_representation(self, instance):
        return super(
            OrganizationRetrieveSerializer,
            self).to_representation(instance)


class OrganizationInviteSerializer(serializers.Serializer):
    email = fields.EmailField(validators=[validators.InviteEmailValidator()])

    class Meta:
        fields = ['email']


class OrganizationInviteUserPublicRetrieveSerializer(
        ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()

    class Meta:
        model = User
        fields = ['uuid', 'name', 'email', 'avatar', 'slug']


class OrganizationInviteRetrieveSerializer(ChannelRelationshipSerializer):
    invitator = OrganizationInviteUserPublicRetrieveSerializer()
    invited = OrganizationInviteUserPublicRetrieveSerializer()

    class Meta:
        model = models.OrganizationInvite
        fields = ['invitator', 'invited']


class MemberRemoveSerializer(serializers.Serializer):
    email = fields.EmailField(validators=[validators.InviteEmailValidator()])

    class Meta:
        fields = ['email']


class MemberListRetrieveSerializer(ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()

    class Meta:
        model = User
        fields = ['id', 'uuid', 'name', 'email', 'avatar', 'slug']


class OrganizationOwnerRetrieveSerializer(ChannelRelationshipSerializer):
    image = UploadedImageSerializer()
    owner = UserOrganizationRetrieveSerializer()
    causes = CauseSerializer(many=True)
    address = address_serializers[1]()

    class Meta:
        model = models.Organization
        fields = [
            'slug',
            'name',
            'description',
            'image',
            'id',
            'owner',
            'causes',
            'address']


class OrganizationMapDataSearchRetrieveSerializer(
        ChannelRelationshipSerializer):
    address = address_serializers[3]()

    class Meta:
        model = models.Organization
        fields = ['slug', 'address']
