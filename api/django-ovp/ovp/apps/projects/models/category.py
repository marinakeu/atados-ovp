from django.db import models
from django.utils.translation import ugettext_lazy as _

from ovp.apps.core.helpers import generate_slug

from ovp.apps.channels.models.abstract import ChannelRelationship


class Category(ChannelRelationship):

    name = models.CharField(_('name'), max_length=150, blank=False, null=False)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    description = models.CharField(
        _('description'),
        max_length=3000,
        blank=True,
        null=True)

    image = models.ForeignKey(
        'uploads.UploadedImage',
        blank=True,
        null=True,
        verbose_name=_('image'),
        related_name="category_image",
        on_delete=models.DO_NOTHING
    )
    highlighted = models.BooleanField(
        _("Highlighted"),
        default=False,
        blank=False
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = generate_slug(
                Category,
                self.name,
                kwargs.get("object_channel", None)
            )
        else:
            self.slug = generate_slug(Category, self.name, self.channel.slug)
        return super().save(*args, **kwargs)

    class Meta:
        app_label = 'projects'
        verbose_name = _('category')
        verbose_name_plural = _('categories')
