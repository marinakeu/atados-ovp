import uuid

from ovp.apps.channels.models import ChannelRelationship

from django.db import models

from django.utils.translation import ugettext_lazy as _


class EmailVerificationToken(ChannelRelationship, models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    token = models.CharField(
        _('Token'),
        max_length=128,
        null=False,
        blank=False)
    created_date = models.DateTimeField(
        _('Created date'),
        auto_now_add=True,
        blank=True,
        null=True)
    used_date = models.DateTimeField(
        _('Used date'), default=None, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = uuid.uuid4()
            self.user.mailing().sendEmailVerification({'token': self})

        super().save(*args, **kwargs)

    class Meta:
        app_label = 'users'
