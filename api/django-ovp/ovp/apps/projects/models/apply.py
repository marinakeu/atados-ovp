from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ovp.apps.projects import emails

from ovp.apps.channels.models.abstract import ChannelRelationship


apply_status_choices = (
    ('applied', 'Applied'),
    ('unapplied', 'Canceled'),
    ('confirmed-volunteer', 'Confirmed Volunteer'),
    ('not-volunteer', 'Not a Volunteer'),
    ('unapplied-by-deactivation', 'Unapplied by deactivation'),
)


class Apply(ChannelRelationship):

    user = models.ForeignKey(
        'users.User',
        blank=True,
        null=True,
        verbose_name=_('user'),
        on_delete=models.DO_NOTHING
    )
    project = models.ForeignKey('projects.Project', verbose_name=_('project'), on_delete=models.DO_NOTHING)
    status = models.CharField(
        _('status'),
        max_length=30,
        choices=apply_status_choices,
        default="applied"
    )
    role = models.ForeignKey(
        'projects.VolunteerRole',
        verbose_name=_('role'),
        blank=False,
        null=True,
        on_delete=models.DO_NOTHING
    )
    date = models.DateTimeField(
        _('created date'),
        auto_now_add=True,
        blank=True
    )
    canceled_date = models.DateTimeField(
        _("canceled date"),
        blank=True,
        null=True
    )

    username = models.CharField(
        _('name'),
        max_length=200,
        blank=True,
        null=True
    )
    email = models.CharField(_('email'), max_length=190, blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=30, blank=True, null=True)
    document = models.CharField(
        _('Documento'),
        max_length=100,
        blank=True,
        null=True
    )
    message = models.TextField(
        _('message'),
        max_length=3000,
        blank=True,
        null=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.status

    def mailing(self, async_mail=None):
        return emails.ApplyMail(self, async_mail)

    def save(self, *args, **kwargs):
        creating = False
        if self.pk is None:
            # Object being created
            creating = True
        else:
            # Object being updated
            if self.__original_status != self.status:
                if self.status == "unapplied":
                    self.canceled_date = timezone.now()
                else:
                    self.canceled_date = None

        return_data = super().save(*args, **kwargs)

        # Emails
        if creating and self.project.closed is False:
            self.mailing().sendAppliedToVolunteer({'apply': self})
            self.mailing().sendAppliedToOwner({'apply': self})
        else:
            if (self.__original_status != self.status
                    and self.status == "unapplied"
                    and self.project.closed is False):
                self.mailing().sendUnappliedToVolunteer({'apply': self})
                self.mailing().sendUnappliedToOwner({'apply': self})

        # Update original values
        self.__original_status = self.status

        if self.role:
            self.role.applied_count = self.role.get_volunteers_numbers()
            self.role.save()

        # Updating project applied_count
        self.project.applied_count = self.project.get_volunteers_numbers()
        self.project.save()

        return return_data

    class Meta:
        app_label = 'projects'
        verbose_name = _('apply')
        verbose_name_plural = _('applies')
        unique_together = (("email", "project"), )
