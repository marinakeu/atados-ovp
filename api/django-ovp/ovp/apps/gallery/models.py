import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.deconstruct import deconstructible


from ovp.apps.channels.models.abstract import ChannelRelationship


class Gallery(ChannelRelationship):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=3000, blank=True, null=True)
    owner = models.ForeignKey('users.User', verbose_name=_('owner'), on_delete=models.DO_NOTHING)
    images = models.ManyToManyField('uploads.UploadedImage')

    # Meta
    deleted = models.BooleanField(_("Deleted"), default=False)
    deleted_date = models.DateTimeField(
        _("Deleted date"),
        blank=True,
        null=True
    )
    created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Modified date'), auto_now=True)

    def __str__(self):
        return str(self.uuid)
