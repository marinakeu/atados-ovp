import vinaigrette

from ovp.apps.core.helpers import generate_slug

from ovp.apps.channels.models import Channel
from ovp.apps.channels.models.abstract import ChannelRelationship

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


# Default causes
CAUSES = [
    'Professional Training',
    'Fight Poverty',
    'Conscious consumption',
    'Culture, Sport and Art',
    'Human Rights',
    'Education',
    'Youth',
    'Elders',
    'Environment',
    'Citizen Participation',
    'Animal Protection',
    'Health',
    'People with disabilities'
]


class Cause(ChannelRelationship):
    name = models.CharField(_('name'), max_length=100)
    image = models.ForeignKey(
        'uploads.UploadedImage',
        blank=True,
        null=True,
        verbose_name=_('image'),
        on_delete=models.DO_NOTHING
    )
    slug = models.SlugField(_('slug'), max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'
        verbose_name = _('cause')
        unique_together = (('slug', 'channel'), )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = generate_slug(
                Cause,
                self.name,
                kwargs.get("object_channel", None)
            )
        super().save(*args, **kwargs)


@receiver(post_save, sender=Channel)
def create_default_skills(sender, instance, **kwargs):
    for cause in CAUSES:
        Cause.objects.create(name=cause, object_channel=instance.slug)


vinaigrette.register(Cause, ['name'])
