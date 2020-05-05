from haystack import indexes
from django.db.models import Q
from ovp.apps.projects.models import Project, Work, Job
from ovp.apps.organizations.models import Organization
from ovp.apps.core.models import GoogleAddress, SimpleAddress
from ovp.apps.users.models import User
from ovp.apps.users.models.profile import get_profile_model
from datetime import datetime
from haystack.fields import EdgeNgramField

"""
Custom search field
"""


class ConfigurableFieldMixin(object):
    def __init__(self, **kwargs):
        self.analyzer = kwargs.pop('analyzer', None)
        super().__init__(**kwargs)


class CustomCharField(ConfigurableFieldMixin, EdgeNgramField):
    pass


"""
Mixins(used by multiple indexes)
"""


class ChannelMixin:
    def prepare_channel(self, obj):
        return obj.channel.slug


class OrganizationMixin:
    def prepare_organization(self, obj):
        return obj.organization.id if obj.organization else 0


class CausesMixin:
    def prepare_causes(self, obj):
        return [cause.id for cause in obj.causes.all()]


class CategoriesMixin:
    def prepare_categories(self, obj):
        return [category.id for category in obj.categories.all()]


class SkillsMixin:
    def prepare_skills(self, obj):
        return [skill.id for skill in obj.skills.all()]


class DateMixin:
    def prepare_end_date(self, obj):
        try:
            if obj.job and obj.job.end_date:
                end_date = obj.job.end_date.strftime('%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

                return end_date
        except Job.DoesNotExist:
            pass

    def prepare_start_date(self, obj):
        try:
            if obj.job and obj.job.start_date:
                start_date = obj.job.start_date.strftime('%Y-%m-%d')
                start_date = datetime.strptime(start_date, '%Y-%m-%d')

                return start_date
        except Job.DoesNotExist:
            pass


class AddressComponentsMixin:
    def prepare_address_components(self, obj):
        types = []

        if obj.address:
            if isinstance(obj.address, GoogleAddress):
                for component in obj.address.address_components.all():
                    for component_type in component.types.all():
                        types.append(
                            u'{}-{}'.format(
                                component.long_name,
                                component_type.name
                            )
                        )

            if isinstance(obj.address, SimpleAddress):
                if obj.address.city:
                    types.append(u'{}-{}'.format(obj.address.city, 'locality'))
                if obj.address.country:
                    types.append(
                        u'{}-{}'.format(obj.address.country, 'country'))

        return types


"""
Indexes
"""


class ProjectIndex(
        indexes.SearchIndex,
        indexes.Indexable,
        SkillsMixin,
        CausesMixin,
        CategoriesMixin,
        AddressComponentsMixin,
        DateMixin,
        ChannelMixin,
        OrganizationMixin):
    name = CustomCharField(model_attr='name')
    causes = indexes.MultiValueField(faceted=True)
    categories = indexes.MultiValueField(faceted=True)
    text = indexes.CharField(document=True, use_template=True)
    skills = indexes.MultiValueField(faceted=True)
    highlighted = indexes.BooleanField(model_attr='highlighted')
    can_be_done_remotely = indexes.BooleanField(faceted=True)
    job = indexes.BooleanField(faceted=True)
    start_date = indexes.DateField(faceted=True, null=True)
    end_date = indexes.DateField(faceted=True, null=True)
    work = indexes.BooleanField(faceted=True)
    published = indexes.BooleanField(model_attr='published')
    deleted = indexes.BooleanField(model_attr='deleted')
    closed = indexes.BooleanField(model_attr='closed')
    skip_address_filter = indexes.BooleanField(
        model_attr='skip_address_filter')
    address_components = indexes.MultiValueField(faceted=True)
    channel = indexes.CharField()
    organization = indexes.IntegerField(faceted=True)
    organization_categories = indexes.MultiValueField(faceted=True)

    def prepare_organization_categories(self, obj):
        if obj.organization:
            return list(
                obj.organization.categories.values_list(
                    'pk', flat=True).distinct())
        return []

    def prepare_job(self, obj):
        job = False

        # Try to get info from job object
        # Need to catch exceptions here because Job has a Project
        try:
            if obj.job:
                job = True
        except Job.DoesNotExist:
            pass

        return job

    def prepare_work(self, obj):
        work = False

        # Try to get info from work object
        # Need to catch exceptions here because Work has a Project
        try:
            if obj.work:
                work = True
        except Work.DoesNotExist:
            pass

        return work

    def prepare_can_be_done_remotely(self, obj):
        can_be_done_remotely = False

        # Try to get info from work object
        # Need to catch exceptions here because Work has a Project
        try:
            can_be_done_remotely = obj.work.can_be_done_remotely
        except Work.DoesNotExist:
            pass

        # Try to get info from job object
        # Need to catch exceptions here because Job has a Project
        try:
            can_be_done_remotely = obj.job.can_be_done_remotely
        except Job.DoesNotExist:
            pass

        return can_be_done_remotely

    def get_model(self):
        return Project

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(deleted=False)


class OrganizationIndex(
        indexes.SearchIndex,
        indexes.Indexable,
        CategoriesMixin,
        CausesMixin,
        AddressComponentsMixin,
        ChannelMixin):
    org_id = indexes.IntegerField(model_attr='id')
    categories = indexes.MultiValueField(faceted=True)
    name = CustomCharField(model_attr='name')
    causes = indexes.MultiValueField(faceted=True)
    text = indexes.CharField(document=True, use_template=True)
    highlighted = indexes.BooleanField(model_attr='highlighted')
    address_components = indexes.MultiValueField(faceted=True)
    published = indexes.BooleanField(model_attr='published')
    deleted = indexes.BooleanField(model_attr='deleted')
    channel = indexes.CharField()
    projects_categories = indexes.MultiValueField(faceted=True)

    def prepare_projects_categories(self, obj):
        return list(
            obj.project_set.all().values_list(
                'categories__pk',
                flat=True).distinct())

    def get_model(self):
        return Organization

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(deleted=False)


class UserIndex(
        indexes.SearchIndex,
        indexes.Indexable,
        AddressComponentsMixin,
        ChannelMixin):
    name = CustomCharField(model_attr='name')
    text = indexes.CharField(document=True)
    causes = indexes.MultiValueField(faceted=True)
    skills = indexes.MultiValueField(faceted=True)
    channel = indexes.CharField()

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        return self.get_model().objects

    def prepare_causes(self, obj):
        try:
            if obj.profile:
                return [cause.id for cause in obj.profile.causes.all()]
        except get_profile_model().DoesNotExist:  # pragma: no cover
            return []

    def prepare_skills(self, obj):
        try:
            if obj.profile:
                return [skill.id for skill in obj.profile.skills.all()]
        except get_profile_model().DoesNotExist:  # pragma: no cover
            return []
