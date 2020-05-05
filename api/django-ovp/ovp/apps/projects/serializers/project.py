from ovp.apps.uploads.serializers import UploadedImageSerializer

from ovp.apps.projects import models
from ovp.apps.projects.decorators import (
    hide_address,
    add_current_user_is_applied_representation
)
from ovp.apps.projects.serializers.disponibility import (
    DisponibilitySerializer,
    add_disponibility_representation
)
from ovp.apps.projects.serializers.job import JobSerializer
from ovp.apps.projects.serializers.work import WorkSerializer
from ovp.apps.projects.serializers.role import (
    VolunteerRoleProjectCreateSerializer,
    VolunteerRoleProjectUpdateSerializer)
from ovp.apps.projects.serializers.apply import ProjectAppliesSerializer
from ovp.apps.projects.serializers.category import (
    CategoryRetrieveSerializer,
    CategoryAssociationSerializer
)
from ovp.apps.core.serializers.post import PostRetrieveSerializer
from ovp.apps.core.serializers.flair import FlairSerializer

from ovp.apps.core import models as core_models
from ovp.apps.core.helpers import get_address_serializers
from ovp.apps.core.serializers.cause import (
    CauseSerializer,
    CauseAssociationSerializer,
    FullCauseSerializer
)
from ovp.apps.core.serializers.skill import (
    SkillSerializer,
    SkillAssociationSerializer
)

from ovp.apps.items.serializers import ItemSerializer

from ovp.apps.organizations.serializers import OrganizationSearchSerializer
from ovp.apps.organizations.serializers import OrganizationRetrieveSerializer
from ovp.apps.organizations.models import Organization

from ovp.apps.uploads.serializers import (
    UploadedImageSerializer,
    UploadedDocumentSerializer,
    UploadedDocumentAssociationSerializer
)

from ovp.apps.gallery.models import Gallery
from ovp.apps.gallery.serializers import (
    GalleryAssociationSerializer,
    GalleryRetrieveSerializer
)

from ovp.apps.uploads.models import UploadedDocument

from ovp.apps.channels.serializers import (
    ChannelRelationshipSerializer,
    ChannelRetrieveSerializer
)
from ovp.apps.channels.cache import get_channel_setting

from ovp.apps.users.serializers import (
    ShortUserPublicRetrieveSerializer,
    UserProjectRetrieveSerializer
)
from ovp.apps.users.models import User

from rest_framework import serializers
from rest_framework import fields
from rest_framework import exceptions
from rest_framework.utils import model_meta


#  Address serializers
address_serializers = get_address_serializers()


##############
#  Validators
##############


def required_organization(request, pk):
    allow_no_org = int(
        get_channel_setting(
            request.channel,
            "CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION"
        )[0]
    )

    if not allow_no_org and not pk and request.method.upper() != "PATCH":
        raise exceptions.ValidationError(
            {'organization': 'This field is required.'}
        )


def project_owner_is_organization_member_or_self(request, organization_pk):
    owner_pk = request.data.get("owner", None)

    if owner_pk and request.user.pk != owner_pk:
        if not organization_pk:
            raise exceptions.ValidationError(
                {'owner': 'Organization field must be set to set owner.'}
            )
        try:
            user = User.objects.get(
                pk=owner_pk,
                organizations_member__pk=organization_pk
            )
        except User.DoesNotExist:
            raise exceptions.ValidationError(
                {'owner': 'User is a not a member of the organization.'}
            )


###############
#  Serializers
###############

class ProjectCreateUpdateSerializer(ChannelRelationshipSerializer):
    address = address_serializers[0]()
    disponibility = DisponibilitySerializer(write_only=True)
    roles = VolunteerRoleProjectUpdateSerializer(many=True, required=False)
    causes = CauseAssociationSerializer(many=True, required=False)
    skills = SkillAssociationSerializer(many=True, required=False)
    categories = CategoryAssociationSerializer(many=True, required=False)
    documents = UploadedDocumentAssociationSerializer(
        many=True, required=False)
    galleries = GalleryAssociationSerializer(many=True, required=False)
    image = UploadedImageSerializer(read_only=True)
    image_id = serializers.IntegerField(required=False)
    organization = OrganizationRetrieveSerializer(read_only=True)
    organization_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)

    class Meta:
        model = models.Project
        fields = [
            'id',
            'image',
            'image_id',
            'name',
            'slug',
            'owner',
            'details',
            'description',
            'highlighted',
            'published',
            'published_date',
            'created_date',
            'address',
            'organization',
            'organization_id',
            'disponibility',
            'roles',
            'max_applies',
            'max_applies_from_roles',
            'minimum_age',
            'hidden_address',
            'crowdfunding',
            'public_project',
            'causes',
            'skills',
            'type',
            'item_id',
            'benefited_people',
            'galleries',
            'testimony',
            'documents',
            'categories'
        ]

        read_only_fields = [
            'slug',
            'highlighted',
            'published',
            'published_date',
            'created_date'
        ]

    def validate(self, data):
        required_organization(
            self.context["request"],
            data.get("organization_id", None)
        )
        project_owner_is_organization_member_or_self(
            self.context["request"],
            data.get("organization_id", None)
        )
        return super().validate(data)

    def create(self, validated_data):
        causes = validated_data.pop('causes', [])
        categories = validated_data.pop('categories', [])
        skills = validated_data.pop('skills', [])
        documents = validated_data.pop('documents', [])
        galleries = validated_data.pop('galleries', [])

        # Address
        address_data = validated_data.pop('address', {})
        address_sr = address_serializers[0](
            data=address_data,
            context=self.context
        )
        address = address_sr.create(address_data)
        validated_data['address'] = address

        # We gotta pop some fields before creating project
        roles = validated_data.pop('roles', [])
        disp = validated_data.pop('disponibility', {})

        # Create project
        project = super().create(validated_data)

        # Roles
        for role_data in roles:
            role_data['project_id'] = project.id
            role_sr = VolunteerRoleProjectCreateSerializer(
                data=role_data,
                context=self.context
            )
            role_sr.is_valid(raise_exception=True)
            role = role_sr.create(role_sr.validated_data)

        # Disponibility
        if disp['type'] == 'work':
            work_data = disp['work']
            work_data['project'] = project
            work_sr = WorkSerializer(data=work_data, context=self.context)
            work = work_sr.create(work_data)

        if disp['type'] == 'job':
            job_data = disp['job']
            job_data['project'] = project
            job_sr = JobSerializer(data=job_data, context=self.context)
            job = job_sr.create(job_data)

        # Associate causes
        for cause in causes:
            c = core_models.Cause.objects.get(pk=cause['id'])
            project.causes.add(c)

        # Associate categories
        for category in categories:
            c = models.Category.objects.get(pk=category['id'])
            project.categories.add(c)

        # Associate galleries
        for gallery in galleries:
            c = Gallery.objects.get(pk=gallery['id'])
            project.galleries.add(c)

        # Associate skills
        for skill in skills:
            s = core_models.Skill.objects.get(pk=skill['id'])
            project.skills.add(s)

        # Associate documents
        for document in documents:
            d = UploadedDocument.objects.get(pk=document['id'])
            project.documents.add(d)

        # Refetch project as signals alter some fields
        return models.Project.objects.get(pk=project.pk)

    def update(self, instance, validated_data):
        causes = validated_data.pop('causes', [])
        skills = validated_data.pop('skills', [])
        categories = validated_data.pop('categories', [])
        documents = validated_data.pop('documents', [])
        galleries = validated_data.pop('galleries', [])
        address_data = validated_data.pop('address', None)
        roles = validated_data.pop('roles', None)
        disp = validated_data.pop('disponibility', None)
        item_id = validated_data.get('item_id', None)

        # Save related resources

        if roles:
            current_roles = list(
                instance.roles.all().values_list(
                    'pk', flat=True))
            instance.roles.clear()
            for role_data in roles:
                identifier = role_data.pop("id") if "id" in role_data else None
                role_data['project_id'] = instance.id

                role_sr = VolunteerRoleProjectUpdateSerializer(
                    data=role_data,
                    context=self.context
                )
                if identifier in current_roles:
                    role_instance = models.VolunteerRole.objects.get(
                        pk=identifier)
                    role = role_sr.update(role_instance, role_data)
                else:
                    role = role_sr.create(role_data)

        if disp:
            models.Work.objects.filter(project=instance).delete()
            models.Job.objects.filter(project=instance).delete()

            if disp['type'] == 'work':
                work_data = disp['work']
                work_data['project'] = instance
                work_sr = WorkSerializer(data=work_data, context=self.context)
                work = work_sr.create(work_data)

            if disp['type'] == 'job':
                job_data = disp['job']
                job_data['project'] = instance
                job_sr = JobSerializer(data=job_data, context=self.context)
                job = job_sr.create(job_data)

        # Associate causes
        if causes:
            instance.causes.remove(
                *core_models.Cause.objects.filter(
                    channel__slug=self.context["request"].channel
                )
            )
            for cause in causes:
                c = core_models.Cause.objects.get(pk=cause['id'])
                instance.causes.add(c)

        # Associate categories
        if categories:
            instance.categories.remove(
                *models.Category.objects.filter(
                    channel__slug=self.context["request"].channel
                )
            )
            for category in categories:
                c = models.Category.objects.get(pk=category['id'])
                instance.categories.add(c)

        # Associate skills
        if skills:
            instance.skills.remove(
                *core_models.Skill.objects.filter(
                    channel__slug=self.context["request"].channel
                )
            )
            for skill in skills:
                s = core_models.Skill.objects.get(pk=skill['id'])
                instance.skills.add(s)

        # Associate galleries
        if galleries:
            instance.galleries.remove(
                *Gallery.objects.filter(
                    channel__slug=self.context["request"].channel
                )
            )
            for gallery in galleries:
                g = Gallery.objects.get(pk=gallery['id'])
                instance.galleries.add(g)

        # Associate documents
        if documents:
            instance.documents.remove(
                *UploadedDocument.objects.filter(
                    channel__slug=self.context["request"].channel
                )
            )
            for document in documents:
                d = UploadedDocument.objects.get(pk=document['id'])
                instance.documents.add(d)

        # Refetch project as signals alter some fields
        instance = models.Project.objects.get(pk=instance.pk)

        instance.item_id = item_id

        if address_data:
            address_sr = address_serializers[0](
                data=address_data,
                context=self.context
            )
            address = address_sr.create(address_data)
            instance.address = address

        return super().update(instance, validated_data)

    @add_disponibility_representation
    def to_representation(self, instance):
        return super().to_representation(instance)


class ProjectRetrieveSerializer(ChannelRelationshipSerializer):
    image = UploadedImageSerializer()
    address = address_serializers[1]()
    organization = OrganizationSearchSerializer()
    disponibility = DisponibilitySerializer(required=False)
    roles = VolunteerRoleProjectCreateSerializer(many=True)
    owner = UserProjectRetrieveSerializer()
    applies = ProjectAppliesSerializer(many=True, source="active_apply_set")
    causes = FullCauseSerializer(many=True)
    flairs = FlairSerializer(many=True)
    skills = SkillSerializer(many=True)
    galleries = GalleryRetrieveSerializer(many=True)
    documents = UploadedDocumentSerializer(many=True)
    categories = CategoryRetrieveSerializer(many=True)
    posts = serializers.SerializerMethodField('get_posts_list')
    is_bookmarked = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()
    item = ItemSerializer()
    channel = ChannelRetrieveSerializer()

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
            'disponibility',
            'roles',
            'owner',
            'minimum_age',
            'applies',
            'applied_count',
            'max_applies',
            'max_applies_from_roles',
            'closed',
            'closed_date',
            'published',
            'hidden_address',
            'crowdfunding',
            'public_project',
            'causes',
            'skills',
            'flairs',
            'categories',
            'posts',
            'is_bookmarked',
            'bookmark_count',
            'item',
            'type',
            'rating',
            'benefited_people',
            'chat_enabled',
            'canceled',
            'channel',
            'galleries',
            'documents'
        ]

    def get_is_bookmarked(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            return instance.is_bookmarked(user)
        return False

    def get_bookmark_count(self, instance):
        is_bookmark_count_enabled = int(
            get_channel_setting(
                self.context['request'].channel,
                "ENABLE_PROJECT_BOOKMARK_COUNT"
            )[0]
        )

        if is_bookmark_count_enabled:
            return instance.bookmark_count()

        return None

    def get_posts_list(self, instance):
        posts = instance.posts.filter(deleted=False).order_by("-pk")
        return PostRetrieveSerializer(
            posts,
            many=True,
            context=self.context
        ).data

    @add_current_user_is_applied_representation
    @hide_address
    @add_disponibility_representation
    def to_representation(self, instance):
        return super().to_representation(instance)


class ProjectManageableRetrieveSerializer(ProjectRetrieveSerializer):

    unrated_users_count = serializers.SerializerMethodField()

    def get_unrated_users_count(self, obj):
        if obj.owner:
            return obj.owner.rating_requests.filter(
                deleted_date=None,
                rating=None,
                content_type__model="user",
                initiator_type__model="project",
                initiator_id=obj.pk
            ).count()
        return 0

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
            'disponibility',
            'roles',
            'owner',
            'minimum_age',
            'applies',
            'applied_count',
            'max_applies',
            'max_applies_from_roles',
            'closed',
            'closed_date',
            'published',
            'hidden_address',
            'crowdfunding',
            'public_project',
            'causes',
            'flairs',
            'posts',
            'skills',
            'categories',
            'is_bookmarked',
            'bookmark_count',
            'item',
            'type',
            'rating',
            'unrated_users_count',
            'benefited_people',
            'chat_enabled',
            'canceled',
            'channel',
            'galleries',
            'documents'
        ]


class ProjectManageableSerializer(ProjectRetrieveSerializer):

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
            'disponibility',
            'roles',
            'owner',
            'minimum_age',
            'closed',
            'closed_date',
            'published',
            'hidden_address',
            'crowdfunding',
            'public_project',
            'causes',
            'skills',
            'flairs',
            'categories',
            'item',
            'rating',
            'type',
            'canceled'
            'max_applies_from_roles',
        ]


class CompactOrganizationSerializer(serializers.ModelSerializer):
    address = address_serializers[2]()

    class Meta:
        model = Organization
        fields = ['name', 'address', 'slug']


class ProjectOnOrganizationRetrieveSerializer(ChannelRelationshipSerializer):

    image = UploadedImageSerializer()
    address = address_serializers[1]()
    disponibility = DisponibilitySerializer(required=False)
    causes = CauseSerializer(many=True)
    flairs = FlairSerializer(many=True)
    skills = SkillSerializer(many=True)
    owner = UserProjectRetrieveSerializer()
    organization = CompactOrganizationSerializer()

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
            'disponibility',
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
            'causes',
            'skills',
            'flairs',
            'owner',
            'organization',
            'rating'
        ]

    @hide_address
    @add_disponibility_representation
    def to_representation(self, instance):
        return super().to_representation(instance)


class ProjectSearchSerializer(ChannelRelationshipSerializer):
    image = UploadedImageSerializer()
    address = address_serializers[1]()
    organization = CompactOrganizationSerializer()
    owner = ShortUserPublicRetrieveSerializer()
    disponibility = DisponibilitySerializer(required=False)
    categories = CategoryRetrieveSerializer(many=True)
    is_bookmarked = serializers.BooleanField()
    causes = FullCauseSerializer(many=True)
    skills = SkillSerializer(many=True)
    channel = ChannelRetrieveSerializer()

    class Meta:
        model = models.Project
        fields = [
            'slug',
            'image',
            'name',
            'description',
            'disponibility',
            'highlighted',
            'published_date',
            'address',
            'organization',
            'owner',
            'applied_count',
            'max_applies',
            'max_applies_from_roles',
            'hidden_address',
            'categories',
            'is_bookmarked',
            'published',
            'closed',
            'closed_date',
            'causes',
            'skills',
            'rating',
            'chat_enabled',
            'canceled',
            'channel'
        ]

    @hide_address
    @add_disponibility_representation
    def to_representation(self, instance):
        return super().to_representation(instance)


class ProjectMapDataSearchRetrieveSerializer(ChannelRelationshipSerializer):

    address = address_serializers[3]()

    class Meta:
        model = models.Project
        fields = ['slug', 'address']
