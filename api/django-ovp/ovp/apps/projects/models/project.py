from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ovp.apps.core.helpers import get_address_model

from ovp.apps.core.helpers import generate_slug

from ovp.apps.projects import emails
from ovp.apps.projects.models.apply import Apply
from ovp.apps.ratings.mixins import RatedModelMixin
from ovp.apps.ratings.models import RatingRequest
from django.contrib.contenttypes.fields import GenericRelation


from ovp.apps.channels.models import ChannelRelationship

import urllib.request as request

import json


types = (
    (1, 'Normal'),
    (2, 'Donation')
)


class Project(ChannelRelationship, RatedModelMixin):
    """
    Project model
    """
    image = models.ForeignKey(
        'uploads.UploadedImage',
        blank=True,
        null=True,
        verbose_name=_('image'),
        on_delete=models.DO_NOTHING
    )
    address = models.ForeignKey(
        get_address_model(),
        blank=True,
        null=True,
        verbose_name=_('address'),
        db_constraint=False,
        on_delete=models.DO_NOTHING
    )
    skills = models.ManyToManyField(
        'core.Skill',
        verbose_name=_('skills')
    )
    causes = models.ManyToManyField(
        'core.Cause',
        verbose_name=_('causes')
    )
    galleries = models.ManyToManyField(
        'gallery.Gallery',
        verbose_name=_('galleries'),
        blank=True
    )
    posts = models.ManyToManyField(
        'core.Post',
        verbose_name=_('posts'),
        blank=True
    )
    documents = models.ManyToManyField(
        'uploads.UploadedDocument',
        verbose_name=_('documents'),
        blank=True
    )

    # Relationships
    categories = models.ManyToManyField(
        'projects.Category',
        verbose_name=_('categories'),
        blank=True
    )
    owner = models.ForeignKey(
        'users.User',
        verbose_name=_('owner'),
        on_delete=models.DO_NOTHING
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        blank=True,
        null=True,
        verbose_name=_('organization'),
        on_delete=models.DO_NOTHING
    )
    item = models.ForeignKey(
        'items.Item',
        blank=True,
        null=True,
        verbose_name=_('item'),
        on_delete=models.DO_NOTHING
    )
    rating_requests = GenericRelation(
        RatingRequest,
        related_query_name='rated_object_project'
    )
    flairs = models.ManyToManyField(
        'core.Flair',
        verbose_name=_('flairs'),
        related_name="projects",
        blank=True
    )

    # Fields
    name = models.CharField(_('Project name'), max_length=100)
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True)
    published = models.BooleanField(_("Published"), default=False)
    highlighted = models.BooleanField(
        _("Highlighted"),
        default=False,
        blank=False
    )
    applied_count = models.IntegerField(
        _('Applied count'),
        blank=False,
        null=False,
        default=0
    )
    max_applies = models.IntegerField(blank=False, null=False, default=1)

    #  This is not a hard limit, just an estimate based on roles vacancies
    max_applies_from_roles = models.IntegerField(
        blank=False,
        null=False,
        default=0
    )
    public_project = models.BooleanField(
        _("Public"),
        default=True,
        blank=False
    )
    minimum_age = models.IntegerField(
        _("Minimum Age"),
        blank=False,
        null=False,
        default=0
    )
    hidden_address = models.BooleanField(_('Hidden address'), default=False)
    crowdfunding = models.BooleanField(_('Crowdfunding'), default=False)
    skip_address_filter = models.BooleanField(
        _('Skip address filter'),
        default=False
    )
    type = models.FloatField(
        _('Project Type'),
        choices=types,
        default=1,
        max_length=10
    )
    benefited_people = models.IntegerField(blank=True, null=True, default=0)
    partnership = models.BooleanField(_('Partnership'), default=False)
    chat_enabled = models.BooleanField(_('Chat Enabled'), default=False)
    canceled = models.BooleanField(_("Canceled"), default=False)
    testimony = models.TextField(
        _('testimony'),
        max_length=3000,
        blank=True,
        null=True
    )

    #  Date fields
    published_date = models.DateTimeField(
        _("Published date"),
        blank=True,
        null=True
    )
    closed = models.BooleanField(_("Closed"), default=False)
    closed_date = models.DateTimeField(_("Closed date"), blank=True, null=True)
    canceled_date = models.DateTimeField(
        _("Canceled date"),
        blank=True,
        null=True
    )
    deleted = models.BooleanField(_("Deleted"), default=False)
    deleted_date = models.DateTimeField(
        _("Deleted date"),
        blank=True,
        null=True
    )
    created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Modified date'), auto_now=True)

    # About
    details = models.TextField(_('Details'), max_length=3000)
    description = models.TextField(
        _('Short description'),
        max_length=160,
        blank=True,
        null=True
    )

    """
    Set this property to use in haystack template
    """
    @property
    def roles_title(self):
        return [role.name for role in self.roles.all()]

    def mailing(self, async_mail=None):
        return emails.ProjectMail(self, async_mail)

    def admin_mailing(self, async_mail=None):
        return emails.ProjectAdminMail(self, async_mail)

    '''
    Data methods
    '''

    def get_phone(self):
        return self.owner.phone

    def get_email(self):
        return self.owner.email

    def get_volunteers_numbers(self):
        return Apply.objects.filter(
            project=self,
            status__in=["applied", "confirmed-volunteer"]
        ).count()

    def is_bookmarked(self, user):
        return self.bookmarks.filter(user=user).count() > 0

    def bookmark_count(self):
        return self.bookmarks.count()

    '''
    Model operation methods
    '''

    def save(self, *args, **kwargs):
        creating = False

        if self.pk is not None:
            orig = Project.objects.get(pk=self.pk)
            if not orig.published and self.published:
                try:
                    self.published_date = timezone.now()
                    self.mailing().sendProjectPublished({'project': self})
                except Exception:
                    pass

            if not orig.closed and self.closed:
                try:
                    self.closed_date = timezone.now()
                    self.mailing().sendProjectClosed({'project': self})
                except Exception:
                    pass

            if not orig.canceled and self.canceled:
                self.closed_date = timezone.now()

            if not orig.deleted and self.deleted:
                self.deleted_date = timezone.now()
        else:
            # Project being created
            self.slug = generate_slug(Project, self.name)
            creating = True

        # If there is no description, take 100 chars from the details
        if not self.description:
            if len(self.details) > 100:
                self.description = self.details[0:100]
            else:
                self.description = self.details

        self.modified_date = timezone.now()

        obj = super().save(*args, **kwargs)

        if creating:
            self.mailing().sendProjectCreated({'project': self})
            try:
                self.admin_mailing().sendProjectCreated({'project': self})
            except Exception:
                pass

        return obj

    def active_apply_set(self):
        return self.apply_set.filter(
            status__in=["applied", "confirmed-volunteer"]
        )

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        app_label = 'projects'
        verbose_name = _('project')
        verbose_name_plural = _('projects')


class VolunteerRole(ChannelRelationship):
    """
    Volunteer role model
    """
    name = models.CharField(
        _('Role name'),
        max_length=50,
        blank=True,
        null=True,
        default=None
    )
    prerequisites = models.TextField(
        _('Prerequisites'),
        max_length=1024,
        blank=True,
        null=True,
        default=None
    )
    details = models.TextField(
        _('Details'),
        max_length=1024,
        blank=True,
        null=True,
        default=None
    )
    vacancies = models.PositiveSmallIntegerField(
        _('Vacancies'),
        blank=True,
        null=True,
        default=None
    )
    project = models.ForeignKey(
        Project,
        blank=True,
        null=True,
        related_name='roles',
        verbose_name=_('Project'),
        on_delete=models.DO_NOTHING
    )
    applied_count = models.IntegerField(
        _('Applied count'),
        blank=False,
        null=False,
        default=0
    )

    class Meta:
        app_label = 'projects'
        verbose_name = _('volunteer role')
        verbose_name_plural = _('volunteer roles')

    def __str__(self):
        return '{0} - {1} - {2} ({3} vacancies)'.format(
            self.name,
            self.details,
            self.prerequisites,
            self.vacancies
        )

    def get_volunteers_numbers(self):
        return Apply.objects.filter(
            role=self,
            project=self.project,
            status__in=["applied", "confirmed-volunteer"]
        ).count()


@receiver(post_save, sender=VolunteerRole)
@receiver(post_delete, sender=VolunteerRole)
def update_max_applies_from_roles(sender, **kwargs):
    if not kwargs.get('raw', False):
        try:
            project = kwargs['instance'].project
        except Project.DoesNotExist:
            return False

        if project:
            queryset = VolunteerRole.objects.filter(project=project)
            vacancies = queryset.aggregate(Sum('vacancies'))
            vacancies = vacancies.get('vacancies__sum')
            Project.objects.filter(pk=project.pk).update(max_applies_from_roles=vacancies if vacancies else 0)

@receiver(post_delete, sender=Apply)
def update_applied_count_on_apply_delete(sender, **kwargs):
    if not kwargs.get('raw', False):
        try:
            project = kwargs['instance'].project
        except Project.DoesNotExist:
            return False

        if project:
            project.applied_count = project.get_volunteers_numbers()
            project.save()
