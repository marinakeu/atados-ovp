from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ovp.apps.channels.models.abstract import ChannelRelationship


class Post(ChannelRelationship):
    title = models.CharField(_('title'), max_length=300, blank=True, null=True)
    content = models.TextField(_('content'), max_length=3000)
    user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.DO_NOTHING)
    reply_to = models.ForeignKey(
        'Post',
        verbose_name=_('reply'),
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING
    )
    published = models.BooleanField('Published', default=True)
    deleted = models.BooleanField('Deleted', default=False)
    created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Modified date'), auto_now=True)
    deleted_date = models.DateTimeField(
        _('Deleted date'),
        editable=False,
        null=True
    )
    gallery = models.ForeignKey(
        'gallery.Gallery',
        verbose_name=_('gallery'),
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING
    )

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Post #{} - by {}".format(self.pk, self.user.name)

    def save(self, *args, **kwargs):
        creating = False

        if self.pk is not None:
            orig = Post.objects.get(pk=self.pk)

            if not orig.deleted and self.deleted:
                self.deleted_date = timezone.now()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_date = timezone.now()
        self.save()
