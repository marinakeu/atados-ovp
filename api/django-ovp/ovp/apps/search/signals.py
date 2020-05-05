from django.db import models
from haystack import signals

from ovp.apps.projects.models import Project, Job, Work
from ovp.apps.organizations.models import Organization
from ovp.apps.core.models import GoogleAddress
from ovp.apps.users.models import User
from ovp.apps.users.models.profile import get_profile_model


class TiedModelRealtimeSignalProcessor(signals.BaseSignalProcessor):
    """
    TiedModelRealTimeSignalProcessor handles updates to a index tied to a model

    We need to be able to detect changes to a model a rebuild another index,
    such as detecting changes to GoogleAddress and updating the index
    for projects and organizations.

    """
    attach_to = {
        Project: ('handle_project_save', 'handle_project_delete'),
        Organization: (
            'handle_organization_save',
            'handle_organization_delete'
        ),
        User: ('handle_save', 'handle_delete'),
        get_profile_model(): ('handle_profile_save', 'handle_profile_delete'),
        GoogleAddress: ('handle_address_save', 'handle_address_delete'),
        Job: ('handle_job_and_work_save', 'handle_job_and_work_delete'),
        Work: ('handle_job_and_work_save', 'handle_job_and_work_delete'),
    }
    m2m = [
        Project.causes.through,
        Project.categories.through,
        Project.skills.through,
        Organization.causes.through
    ]

    m2m_user = [
        get_profile_model().causes.through,
        get_profile_model().skills.through
    ]

    def setup(self):
        for model, functions in self.attach_to.items():
            models.signals.post_save.connect(
                getattr(self, functions[0]), sender=model)
            models.signals.post_delete.connect(
                getattr(self, functions[1]), sender=model)

        for item in self.m2m:
            models.signals.m2m_changed.connect(self.handle_m2m, sender=item)

        for item in self.m2m_user:
            models.signals.m2m_changed.connect(
                self.handle_m2m_user, sender=item)

    # never really called
    def teardown(self):  # pragma: no cover
        for item in self.attach_to:
            models.signals.post_save.disconnect(
                getattr(self, item[1]), sender=item[0])
            models.signals.post_delete.disconnect(
                getattr(self, item[2]), sender=item[0])

        for item in self.m2m:
            models.signals.m2m_changed.disconnect(self.handle_m2m, sender=item)

        for item in self.m2m_user:
            models.signals.m2m_changed.disconnect(
                self.handle_m2m_user, sender=item)

    def handle_organization_save(self, sender, instance, **kwargs):
        """ Custom handler for organization save """
        self.handle_save(instance.__class__, instance)

        # We reindex projects, as it index information about
        # organization(organization categories)
        for prj in instance.project_set.all():
            self.handle_save(prj.__class__, prj)

    def handle_organization_delete(self, sender, instance, **kwargs):
        """ Custom handler for organization delete """
        self.handle_delete(instance.__class__, instance)

    def handle_project_save(self, sender, instance, **kwargs):
        """ Custom handler for project save """
        # We reindex organization, as it index information about
        # projects(projects categories)
        if instance.organization:
            self.handle_save(
                instance.organization.__class__,
                instance.organization)

        self.handle_save(instance.__class__, instance)

    def handle_project_delete(self, sender, instance, **kwargs):
        """ Custom handler for project delete """
        self.handle_delete(instance.__class__, instance)

        try:
            if instance.organization:
                self.handle_save(
                    instance.organization.__class__,
                    instance.organization)
        except Organization.DoesNotExist:
            pass  # just returns, instance already deleted from database

    def handle_address_save(self, sender, instance, **kwargs):
        """ Custom handler for address save """
        objects = self.find_associated_with_address(instance)
        for obj in objects:
            self.handle_save(obj.__class__, obj)

    # this function is never really called on sqlite dbs
    def handle_address_delete(self, sender, instance, **kwargs):
        """ Custom handler for address delete """
        objects = self.find_associated_with_address(instance)

        # this is not called as django will delete associated project/address
        # triggering handle_delete
        for obj in objects:  # pragma: no cover
            self.handle_delete(obj.__class__, obj)

    def handle_job_and_work_save(self, sender, instance, **kwargs):
        """ Custom handler for job and work save """
        self.handle_save(instance.project.__class__, instance.project)

    def handle_job_and_work_delete(self, sender, instance, **kwargs):
        """ Custom handler for job and work delete """
        self.handle_delete(instance.project.__class__, instance.project)

    def handle_profile_save(self, sender, instance, **kwargs):
        """ Custom handler for user profile save """
        self.handle_save(instance.user.__class__, instance.user)

    def handle_profile_delete(self, sender, instance, **kwargs):
        """ Custom handler for user profile delete """
        try:
            self.handle_save(
                instance.user.__class__,
                instance.user)  # we call save just as well
        except (get_profile_model().DoesNotExist):
            pass  # just returns, instance already deleted from database
        except User.DoesNotExist:
            pass  # just returns, instance already deleted from database

    def handle_m2m(self, sender, instance, **kwargs):
        """ Handle many to many relationships """
        if self.attach_to.get(instance.__class__, None):
            getattr(self, self.attach_to[instance.__class__][0])(
                instance.__class__, instance)
        else:
            self.handle_save(instance.__class__, instance)

    def handle_m2m_user(self, sender, instance, **kwargs):
        """ Handle many to many relationships for user field """
        self.handle_save(instance.user.__class__, instance.user)

    def find_associated_with_address(self, instance):
        """
        Returns list with projects and organizations associated
        with given address
        """
        objects = []
        objects += list(Project.objects.filter(address=instance))
        objects += list(Organization.objects.filter(address=instance))

        return objects
