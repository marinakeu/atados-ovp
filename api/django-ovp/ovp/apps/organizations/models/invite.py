
from django.db import models

from ovp.apps.channels.models.abstract import ChannelRelationship

from django.utils.translation import ugettext_lazy as _


class OrganizationInvite(ChannelRelationship):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.DO_NOTHING)
    invitator = models.ForeignKey("users.User", related_name="has_invited", on_delete=models.DO_NOTHING)
    invited = models.ForeignKey("users.User", related_name="been_invited", on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(
        _('Joined date'),
        auto_now_add=True,
        null=True,
        blank=True)
    revoked_date = models.DateTimeField(
        _('Modified date'), default=None, null=True, blank=True)
    joined_date = models.DateTimeField(
        _('Joined date'), default=None, null=True, blank=True)

    class Meta:
        app_label = 'organizations'
        verbose_name = _('organization_invite')
