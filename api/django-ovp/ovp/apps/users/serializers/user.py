from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils import timezone

from ovp.apps.core.serializers.flair import FlairSerializer

from ovp.apps.users import models
from ovp.apps.users.helpers import get_settings, import_from_string
from ovp.apps.users.models.profile import get_profile_model
from ovp.apps.users.serializers.profile import get_profile_serializers
from ovp.apps.users.serializers.profile import ProfileSearchSerializer
from ovp.apps.users.validators import PasswordReuse
from ovp.apps.users.decorators import expired_password
from ovp.apps.organizations.serializers import (
    OrganizationSearchSerializer, OrganizationOwnerRetrieveSerializer
)

from ovp.apps.projects.serializers.apply_user import (
    ApplyUserRetrieveSerializer
)
from ovp.apps.projects.serializers.bookmark_user import (
    BookmarkUserRetrieveSerializer
)
from ovp.apps.projects.models.apply import Apply

from ovp.apps.uploads.serializers import UploadedImageSerializer

from ovp.apps.channels.serializers import ChannelRelationshipSerializer
from ovp.apps.channels.cache import get_channel_setting

from ovp.apps.ratings.serializers import RatingRequestRetrieveSerializer

from rest_framework import serializers
from rest_framework import permissions
from rest_framework import fields
from rest_framework import validators


class UserCreateSerializer(ChannelRelationshipSerializer):
    profile = get_profile_serializers()[0](required=False)
    slug = serializers.CharField(read_only=True)
    uuid = serializers.CharField(read_only=True)

    class Meta:
        model = models.User
        fields = [
            'uuid',
            'name',
            'email',
            'password',
            'phone',
            'phone2',
            'avatar',
            'locale',
            'profile',
            'public',
            'slug',
            'is_subscribed_to_newsletter',
            'document'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        errors = dict()

        if data.get('password'):
            password = data.get('password', '')
            try:
                validate_password(password=password)
            except ValidationError as e:
                errors['password'] = list(
                    map(lambda x: [x.code, x.message], e.error_list))

        if data.get('email'):
            data['email'] = data.get('email', '').lower()
            users = models.User.objects.filter(
                email__iexact=data['email'], channel__slug=self.context["request"].channel
            )
            if users.count():
                msg = "An user with this email is already registered."
                errors['email'] = msg

        s = get_settings()
        validation_functions = s.get('USER_REGISTER_VALIDATION_FUNCTIONS', [])
        for func_string in validation_functions:
            func = import_from_string(func_string)
            out = func(data, self.context)
            if out:
                errors = {**errors, **out}
                break

        if errors:
            raise serializers.ValidationError(errors)

        return super().validate(data)

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})

        # Create user
        user = super().create(validated_data)

        # Profile
        profile_data['user'] = user
        profile_sr = get_profile_serializers()[0](
            data=profile_data, context=self.context)
        profile = profile_sr.create(profile_data)

        return user


class UserUpdateSerializer(UserCreateSerializer):
    password = fields.CharField(write_only=True, validators=[PasswordReuse()])
    current_password = fields.CharField(write_only=True)
    profile = get_profile_serializers()[0](required=False)

    class Meta:
        model = models.User
        permission_classes = (permissions.IsAuthenticated,)
        fields = [
            'name',
            'phone',
            'phone2',
            'password',
            'avatar',
            'current_password',
            'locale',
            'profile',
            'public',
            'is_subscribed_to_newsletter',
            'document'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        errors = dict()

        if data.get('password') or data.get('current_password'):
            current_password = data.pop('current_password', '')
            password = data.get('password', '')

            try:
                validate_password(password=password)
            except ValidationError as e:
                errors['password'] = list(
                    map(lambda x: [x.code, x.message], e.error_list))

            if not authenticate(
                    email=self.context['request'].user.email,
                    password=current_password,
                    channel=self.context["request"].channel):
                errors['current_password'] = ["Invalid password."]

        if errors:
            raise serializers.ValidationError(errors)

        return super().validate(data)

    def update(self, instance, data):
        ProfileModel = get_profile_model()
        profile_data = data.pop('profile', None)

        if profile_data:
            has_profile = False
            try:
                if instance.profile:
                    has_profile = True
                else:
                    has_profile = False
            except models.UserProfile.DoesNotExist:
                has_profile = False

            if has_profile:
                profile = instance.profile
            else:
                profile = ProfileModel(user=instance)
                profile.save(object_channel=self.context["request"].channel)

            profile_sr = get_profile_serializers()[0](
                profile, data=profile_data, partial=True)
            profile_sr.is_valid(raise_exception=True)
            profile = profile_sr.update(profile, profile_sr.validated_data)

        return super().update(instance, data)


class CurrentUserSerializer(ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()
    profile = get_profile_serializers()[1]()
    organizations = OrganizationOwnerRetrieveSerializer(
        many=True, source='active_organizations')
    rating_requests_user_count = serializers.SerializerMethodField()
    rating_requests_project_count = serializers.SerializerMethodField()
    rating_requests_projects_with_unrated_users = serializers.SerializerMethodField()
    chat_enabled = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = [
            'uuid',
            'name',
            'phone',
            'phone2',
            'avatar',
            'email',
            'locale',
            'profile',
            'slug',
            'public',
            'organizations',
            'rating_requests_user_count',
            'rating_requests_project_count',
            'rating_requests_projects_with_unrated_users',
            'is_subscribed_to_newsletter',
            'chat_enabled',
            'document',
            'is_email_verified',
            'is_staff',
            'is_superuser'
        ]

    def get_chat_enabled(self, obj):
        applies = Apply.objects.filter(
            project__published=True,
            project__chat_enabled=True,
            user=obj
        )
        return applies.count() > 0

    def get_rating_requests_user_count(self, obj):
        return obj.rating_requests.filter(
            deleted_date=None,
            rating=None,
            content_type__model="user").count()

    def get_rating_requests_project_count(self, obj):
        return obj.rating_requests.filter(
            deleted_date=None,
            rating=None,
            content_type__model="project").count()

    def get_rating_requests_projects_with_unrated_users(self, obj):
        return len(
            obj.rating_requests.filter(
                deleted_date=None,
                rating=None,
                content_type__model="user",
                initiator_type__model="project").values_list(
                "initiator_id",
                flat=True).distinct())

    @expired_password
    def to_representation(self, *args, **kwargs):
        return super().to_representation(*args, **kwargs)


class ShortUserPublicRetrieveSerializer(ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()

    class Meta:
        model = models.User
        fields = ['uuid', 'name', 'avatar', 'slug']


class LongUserPublicRetrieveSerializer(ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()
    profile = get_profile_serializers()[1]()
    applies = ApplyUserRetrieveSerializer(many=True, source="apply_set")
    flairs = FlairSerializer(many=True)
    bookmarked_projects = BookmarkUserRetrieveSerializer(
        many=True, source="projectbookmark_set")
    volunteer_hours = serializers.SerializerMethodField()
    donated_to_organizations = OrganizationSearchSerializer(many=True)

    class Meta:
        model = models.User
        fields = [
            'name',
            'avatar',
            'profile',
            'slug',
            'applies',
            'bookmarked_projects',
            'volunteer_hours',
            'rating',
            'flairs',
            'donated_to_organizations']

    def get_volunteer_hours(self, obj):
        volunteer_hours = timezone.timedelta(hours=0)
        applies = Apply.objects.filter(user=obj).all()
        for a in applies:
            if hasattr(a.project, 'job'):
                jobs = a.project.job.dates
                for job in jobs.values():
                    volunteer_hours += job['end_date'] - job['start_date']
            elif hasattr(a.project, 'work'):
                if a.project.closed:
                    last_time = a.project.closed_date
                else:
                    last_time = timezone.now()

                try:
                    weeks = (last_time - a.date).days // 7
                    if a.project.work.weekly_hours is not None:
                        project_hours = a.project.work.weekly_hours
                    else:
                        project_hours = 0
                    project_hours = project_hours * (weeks + 1)
                    volunteer_hours += timezone.timedelta(hours=project_hours)
                except BaseException:
                    pass

        resp = (volunteer_hours.days * 24) + (volunteer_hours.seconds // 3600)
        return resp

    def to_representation(self, *args, **kwargs):
        ret = super().to_representation(*args, **kwargs)
        is_bookmarked_projects_on_user_enabled = int(
            get_channel_setting(
                self.context['request'].channel,
                "ENABLE_PUBLIC_USER_BOOKMARKED_PROJECTS")[0])

        if not is_bookmarked_projects_on_user_enabled:
            ret["bookmarked_projects"] = None

        return ret


class UserProjectRetrieveSerializer(ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()
    flairs = FlairSerializer(many=True)

    class Meta:
        model = models.User
        fields = [
            'uuid',
            'name',
            'avatar',
            'email',
            'phone',
            'phone2',
            'slug',
            'flairs'
        ]


class UserApplyRetrieveSerializer(ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()
    profile = get_profile_serializers()[1]()
    flairs = FlairSerializer(many=True)

    class Meta:
        model = models.User
        fields = [
            'uuid',
            'name',
            'slug',
            'avatar',
            'phone',
            'phone2',
            'email',
            'profile',
            'rating',
            'flairs'
        ]


class UserSearchSerializer(ChannelRelationshipSerializer):
    avatar = UploadedImageSerializer()
    profile = get_profile_serializers()[2]()

    class Meta:
        model = models.User
        fields = ['slug', 'name', 'avatar', 'profile']


def get_user_search_serializer():
    s = get_settings()
    class_path = s.get('USER_SEARCH_SERIALIZER', None)
    if class_path:
        return import_from_string(class_path)
    return UserSearchSerializer
