import vinaigrette

from ovp.apps.core.helpers import generate_slug

from ovp.apps.channels.models import Channel
from ovp.apps.channels.models.abstract import ChannelRelationship

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


# Default skills
SKILLS = [
    'Arts/Handcrafting',
    'Communication',
    'Dance/Music',
    'Law',
    'Education',
    'Sports',
    'Cooking',
    'Management',
    'Idioms',
    'Computers/Technology',
    'Health',
    'Others'
]


class Skill(ChannelRelationship):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'
        verbose_name = _('skill')
        unique_together = (('slug', 'channel'),)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = generate_slug(
                Skill,
                self.name,
                kwargs.get("object_channel", None)
            )
        super().save(*args, **kwargs)


@receiver(post_save, sender=Channel)
def create_default_skills(sender, instance, **kwargs):
    for skill in SKILLS:
        Skill.objects.create(name=skill, object_channel=instance.slug)


vinaigrette.register(Skill, ['name'])
