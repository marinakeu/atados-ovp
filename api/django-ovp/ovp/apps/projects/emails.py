from ovp.apps.core.emails import BaseMail
from django.utils.translation import ugettext_lazy as _
from ovp.apps.channels.cache import get_channel_setting


class ProjectMail(BaseMail):
    """
    This class is responsible for firing emails for Project related actions

    Context should always include a project instance.
    """

    def __init__(self, project, async_mail=None):
        super().__init__(
            project.owner.email,
            channel=project.channel.slug,
            async_mail=async_mail,
            locale=project.owner.locale
        )

    def sendProjectCreated(self, context={}):
        """
        Sent when user creates a project
        """
        return self.sendEmail('projectCreated', 'Project created', context)

    def sendProjectPublished(self, context):
        """
        Sent when project is published
        """
        return self.sendEmail('projectPublished', 'Project published', context)

    def sendProjectClosed(self, context):
        """
        Sent when project gets closed
        """
        return self.sendEmail('projectClosed', 'Project closed', context)


class ApplyMail(BaseMail):
    """
    This class is responsible for firing emails for apply related actions
    """

    def __init__(self, apply, async_mail=None, locale=None):
        self.apply = apply
        self.async_obj = async_mail
        locale = locale or (apply.user and apply.user.locale)
        super().__init__(
            apply.email,
            channel=apply.channel.slug,
            async_mail=async_mail,
            locale=locale
        )

    def sendAppliedToVolunteer(self, context={}):
        """
        Sent to user when he applies to a project
        """
        return self.sendEmail(
            'volunteerApplied-ToVolunteer',
            'Applied to project',
            context
        )

    def sendAppliedToOwner(self, context={}):
        """
        Sent to project owner when user applies to a project
        """
        super().__init__(
            self.apply.project.owner.email,
            channel=self.apply.channel.slug,
            async_mail=self.async_obj,
            locale=self.apply.project.owner.locale
        )
        return self.sendEmail(
            'volunteerApplied-ToOwner',
            'New volunteer',
            context
        )

    def sendUnappliedToVolunteer(self, context={}):
        """
        Sent to user when he unapplies from a project
        """
        return self.sendEmail(
            'volunteerUnapplied-ToVolunteer',
            'Unapplied from project',
            context
        )

    def sendUnappliedToOwner(self, context={}):
        """
        Sent to project owner when user unapplies from a project
        """
        super().__init__(
            self.apply.project.owner.email,
            channel=self.apply.channel.slug,
            async_mail=self.async_obj,
            locale=self.apply.project.owner.locale
        )
        return self.sendEmail(
            'volunteerUnapplied-ToOwner',
            'Volunteer unapplied from project',
            context
        )


class ProjectAdminMail(BaseMail):
    """
    This class is responsible for firing emails for Project related actions
    """

    def __init__(self, project, async_mail=None):
        email = get_channel_setting(organization.channel.slug, "ADMIN_MAIL")[0]
        super().__init__(
            email,
            channel=project.channel.slug,
            async_mail=async_mail
        )

    def sendProjectCreated(self, context={}):
        """
        Sent when user creates a project
        """
        return self.sendEmail(
            'projectCreatedToAdmin',
            'Project created',
            context
        )
