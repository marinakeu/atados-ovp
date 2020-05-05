from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from ovp.apps.core.helpers import generate_slug
from ovp.apps.core.helpers import get_address_model

from ovp.apps.channels.models.abstract import ChannelRelationship

from ovp.apps.organizations.emails import OrganizationMail
from ovp.apps.organizations.emails import OrganizationAdminMail
from ovp.apps.organizations.validators import validate_CNPJ, format_CNPJ

from ovp.apps.donations.models import Seller

from ovp.apps.ratings.mixins import RatedModelMixin

from django.utils.translation import ugettext_lazy as _

ORGANIZATION_TYPES = (
    (0, _('Organization')),
    (1, _('School')),
    (2, _('Company')),
    (3, _('Group of volunteers')),
)


class Organization(ChannelRelationship, RatedModelMixin):
    # Relationships
    owner = models.ForeignKey(
        'users.User',
        verbose_name=_('owner'),
        related_name="organizations",
        on_delete=models.DO_NOTHING
    )
    address = models.OneToOneField(
        get_address_model(),
        blank=True,
        null=True,
        verbose_name=_('address'),
        db_constraint=False,
        on_delete=models.DO_NOTHING)
    image = models.ForeignKey(
        'uploads.UploadedImage',
        blank=True,
        null=True,
        verbose_name=_('image'),
        on_delete=models.DO_NOTHING)
    cover = models.ForeignKey(
        'uploads.UploadedImage',
        blank=True,
        null=True,
        related_name="+",
        verbose_name=_('cover'),
        on_delete=models.DO_NOTHING)
    causes = models.ManyToManyField(
        'core.Cause',
        verbose_name=_('causes'),
        blank=True)
    members = models.ManyToManyField('users.User', verbose_name=_(
        'members'), related_name="organizations_member", blank=True)
    galleries = models.ManyToManyField(
        'gallery.Gallery',
        verbose_name=_('galleries'),
        related_name="galleries",
        blank=True)
    flairs = models.ManyToManyField(
        'core.Flair',
        verbose_name=_('flairs'),
        related_name="organizations",
        blank=True)

    # Fields
    categories = models.ManyToManyField(
        'projects.Category',
        verbose_name=_('categories'),
        blank=True)
    slug = models.SlugField(
        _('Slug'),
        max_length=100,
        unique=True,
        blank=True,
        null=True)
    name = models.CharField(_('Name'), max_length=300)
    website = models.URLField(
        _('Website'),
        blank=True,
        null=True,
        default=None)
    facebook_page = models.CharField(
        _('Facebook'),
        max_length=255,
        blank=True,
        null=True,
        default=None)
    instagram_user = models.CharField(
        _('Instagram'),
        max_length=255,
        blank=True,
        null=True,
        default=None)
    type = models.PositiveSmallIntegerField(
        _('Type'), choices=ORGANIZATION_TYPES, default=0)
    details = models.TextField(
        _('Details'),
        max_length=3000,
        blank=True,
        null=True,
        default=None)
    description = models.CharField(
        _('Short description'),
        max_length=320,
        blank=True,
        null=True)
    hidden_address = models.BooleanField(_('Hidden address'), default=False)
    verified = models.BooleanField(_('Verified'), default=False)
    document = models.CharField(
        _('CNPJ'),
        unique=True,
        max_length=100,
        validators=[validate_CNPJ],
        blank=True,
        null=True)
    benefited_people = models.IntegerField(
        _('Benefited people'), blank=True, null=True, default=0)
    allow_donations = models.BooleanField(_('Allow donations'), default=False)

    # Organization contact
    contact_name = models.CharField(
        _('Responsible name'),
        max_length=150,
        blank=True,
        null=True)
    contact_email = models.EmailField(
        _('Responsible email'),
        max_length=150,
        blank=True,
        null=True)
    contact_phone = models.CharField(
        _('Responsible phone'),
        max_length=150,
        blank=True,
        null=True)

    # Meta
    highlighted = models.BooleanField(
        _('Highlighted'), default=False, blank=False)
    published = models.BooleanField(_('Published'), default=False)
    published_date = models.DateTimeField(
        _('Published date'), blank=True, null=True)
    deleted = models.BooleanField(_('Deleted'), default=False)
    deleted_date = models.DateTimeField(
        _('Deleted date'), blank=True, null=True)
    created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Modified date'), auto_now=True)
    is_inactive = models.BooleanField(
        _('Inactive'), default=False, blank=False)
    reminder_sent = models.BooleanField(
        _('Reminder'), default=False, blank=False)
    reminder_sent_date = models.DateTimeField(
        _('Reminder sent date'), blank=True, null=True)

    @staticmethod
    def autocomplete_search_fields():
        return 'name',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__orig_deleted = self.deleted
        self.__orig_published = self.published

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.published = False
        self.save()

    def mailing(self):
        return OrganizationMail(self)

    def admin_mailing(self):
        return OrganizationAdminMail(self)

    def save(self, *args, **kwargs):
        creating = False
        force_update = True

        if self.pk is not None:
            if not self.__orig_published and self.published:
                self.published_date = timezone.now()
                self.mailing().sendOrganizationPublished(
                    {"organization": self})

            if not self.__orig_deleted and self.deleted:
                self.deleted_date = timezone.now()
        else:
            # Organization being created
            self.slug = generate_slug(Organization, self.name)
            creating = True

        self.document = format_CNPJ(self.document)

        # If there is no description, take 100 chars from the details
        if not self.description and self.details:
            if len(self.details) > 100:
                self.description = self.details[0:100]
            else:
                self.description = self.details

        obj = super().save(*args, **kwargs)

        if creating:
            self.mailing().sendOrganizationCreated({"organization": self})
            try:
                self.admin_mailing().sendOrganizationCreated(
                    {"organization": self})
            except BaseException:
                pass

        return obj

    def is_bookmarked(self, user):
        return self.bookmarks.filter(user=user).count() > 0

    def donators(self):
        User = get_user_model()
        user_pks = set(
            self.transaction_set.filter(
                status='succeeded',
                anonymous=False).values_list(
                'user',
                flat=True))
        qs = User.objects.filter(id__in=user_pks, is_active=True)
        return qs.distinct('pk')

    def get_seller_object(self, backend):
        try:
            return Seller.objects.get(backend=backend, organization=self)
        except Seller.DoesNotExist:
            pass
        return None

    class Meta:
        app_label = 'organizations'
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')
