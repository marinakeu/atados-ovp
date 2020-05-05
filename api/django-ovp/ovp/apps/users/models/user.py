from ovp.apps.users import emails
from ovp.apps.users.models.profile import get_profile_model
from ovp.apps.users.models.password_history import PasswordHistory
from ovp.apps.users.models.email_verification import EmailVerificationToken

from ovp.apps.channels.models import ChannelRelationship
from ovp.apps.channels.models.manager import ChannelRelationshipManager

from ovp.apps.ratings.mixins import RatedModelMixin

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from ovp.apps.ratings.models import RatingRequest
from django.contrib.contenttypes.fields import GenericRelation

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

import uuid
from shortuuid.main import encode as encode_uuid

from random import randint


class UserManager(ChannelRelationshipManager, BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('The given email address must be set.')
        email = UserManager.normalize_email(email)
        user = self.create(email=email, password=password, is_staff=False,
                           is_active=True, last_login=now,
                           joined_date=now, **extra_fields)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save()
        return user

    class Meta:
        app_label = 'ovp_user'


class User(
        ChannelRelationship,
        AbstractBaseUser,
        PermissionsMixin,
        RatedModelMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(_('Email'), max_length=190)
    locale = models.CharField(
        _('Locale'),
        max_length=8,
        null=False,
        blank=True,
        default='en')
    rating_requests = GenericRelation(
        RatingRequest, related_query_name='rated_object_user')
    flairs = models.ManyToManyField(
        'core.Flair',
        verbose_name=_('flairs'),
        related_name="users",
        blank=True)

    # User information
    name = models.CharField(_('Name'), max_length=200, null=False, blank=False)
    slug = models.SlugField(_('Slug'), max_length=100, null=True, blank=True)
    avatar = models.ForeignKey(
        'uploads.UploadedImage',
        blank=False,
        null=True,
        related_name='avatar_user',
        verbose_name=_('avatar'),
        on_delete=models.DO_NOTHING)
    phone = models.CharField(_('Phone'), max_length=30, null=True, blank=True)
    phone2 = models.CharField(
        _('Phone 2'),
        max_length=30,
        null=True,
        blank=True)
    document = models.CharField(
        _('Document'),
        max_length=40,
        null=True,
        blank=True)

    # Flags
    public = models.BooleanField(_('Public'), default=True)
    is_staff = models.BooleanField(_('Staff'), default=False)
    is_superuser = models.BooleanField(_('Superuser'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    is_email_verified = models.BooleanField(_('Email verified'), default=False)
    is_subscribed_to_newsletter = models.BooleanField(
        _('Subscribed to newsletter'), default=True)

    # Meta
    joined_date = models.DateTimeField(
        _('Joined date'),
        auto_now_add=True,
        null=True,
        blank=True)
    modified_date = models.DateTimeField(
        _('Modified date'), auto_now=True, null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    LOGIN = False

    class Meta:
        app_label = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        unique_together = (('email', 'channel'), ('slug', 'channel'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_password = self.password
        self.__original_email = self.email

    def mailing(self, async_mail=None):
        return emails.UserMail(self, async_mail)

    def save(self, *args, **kwargs):
        hash_password = False
        creating = False
        original_password = self.password
        update_email = False

        if not self.pk:
            self.slug = encode_uuid(self.uuid)
            hash_password = True
            creating = True
        else:
            # checks if password has changed and if it was set by set_password
            if (self.__original_password != self.password
                    and not self.check_password(self._password)):
                hash_password = True
            # checks if email has changed
            if self.__original_email != self.email:
                update_email = True

        if hash_password and self.LOGIN is False:
            self.set_password(self.password)  # hash it
            self.__original_password = self.password

        if update_email:
            context = {"name": self.name, "email": self.email}
            self.email = self.__original_email.lower()
            self.mailing().sendUpdateEmail(context)

            self.email = context['email'].lower()
            self.is_email_verified = False
            EmailVerificationToken.objects.create(
                user=self, object_channel=self.channel.slug)

        no_email = kwargs.pop("no_email", False)
        obj = super().save(*args, **kwargs)

        if creating:
            if not no_email:
                self.mailing().sendWelcome()
            EmailVerificationToken.objects.create(
                user=self, object_channel=self.channel.slug)

        return obj

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    @property
    def profile(self):
        model = get_profile_model()
        related_field_name = model._meta.get_field('user').related_query_name()
        try:
            obj = getattr(self, related_field_name, None)
            if isinstance(obj, model):
                return obj
            else:
                return model.objects.get(user=self)
        except model.DoesNotExist:
            return None

    def active_organizations(self):
        Organization = apps.get_model('organizations', 'Organization')
        qs = self.organizations_member.filter(
            deleted=False) | Organization.objects.filter(
            deleted=False, owner=self)
        return qs.distinct('pk')

    def donated_to_organizations(self):
        Organization = apps.get_model('organizations', 'Organization')
        org_pks = set(
            self.transaction_set.filter(
                status='succeeded',
                anonymous=False).values_list(
                'organization',
                flat=True))
        qs = Organization.objects.filter(id__in=org_pks)
        return qs.distinct('pk')

    @staticmethod
    def autocomplete_search_fields():
        return 'name',

    @staticmethod
    def autocomplete_search_queryset(qs, cleaned_data):
        try:
            from gpa.models import GPAUserProfile

            profile_pks = list(
                GPAUserProfile.objects.filter(
                    collaborator_code__icontains=cleaned_data.get('q')
                ).values_list(flat=True))

            qs = qs.filter(Q(name__icontains=cleaned_data.get('q')) | Q(
                users_userprofile_profile__pk__in=profile_pks))
        except ImportError:
            pass
        return qs

    def __str__(self):
        # TODO: Move this outside OVP, need to reimplement user model checking
        # everywhere
        if (hasattr(self, 'profile')
                and hasattr(self.profile, 'collaborator_code')):
            return "#{} - {}".format(self.profile.collaborator_code, self.name)
        return self.name

    def clean(self):
        if self.pk:
            if User.objects.filter(
                    email__iexact=self.email,
                    channel=self.channel).exclude(
                    pk=self.pk).count():
                raise ValidationError(
                    "There's already an user with email {}.".format(
                        self.email))
        return super(User, self).clean()


@receiver(post_save, sender=User)
def update_history(sender, instance, raw=False, **kwargs):
    if raw:  # pragma: no cover
        return

    last_password = PasswordHistory.objects.filter(
        user=instance, channel=instance.channel).last()

    if not last_password or last_password.hashed_password != instance.password:
        PasswordHistory(
            hashed_password=instance.password,
            user=instance).save(
            object_channel=instance.channel.slug)
