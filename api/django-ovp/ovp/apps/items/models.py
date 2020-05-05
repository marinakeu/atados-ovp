from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.models import ChannelRelationship

from ckeditor.fields import RichTextField


class Item(ChannelRelationship):
    """
    Item model
    """
    name = models.CharField(
        _('Item name'),
        blank=True,
        null=True,
        max_length=100)
    about = RichTextField(_('About'), blank=True, null=True, max_length=3000)
    deleted = models.BooleanField(_("Deleted"), default=False)
    # Date fields
    created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Modified date'), auto_now=True)
    deleted_date = models.DateTimeField(
        _("Deleted date"), blank=True, null=True)

    def save(self, *args, **kwargs):
        self.modified_date = timezone.now()
        return super(Item, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_date = timezone.now()
        self.save()

    class Meta:
        app_label = 'items'
        verbose_name = _('item')
        verbose_name_plural = _('items')


class ItemImage(ChannelRelationship):
    """
    ItemImage model
    """
    image = models.ForeignKey(
        'uploads.UploadedImage',
        blank=True,
        null=True,
        verbose_name=_('image'),
        on_delete=models.DO_NOTHING)
    item = models.ForeignKey(
        'Item',
        models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_('item'))
    deleted = models.BooleanField(_("Deleted"), default=False)
    # Date fields
    created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Modified date'), auto_now=True)
    deleted_date = models.DateTimeField(
        _("Deleted date"), blank=True, null=True)

    def save(self, *args, **kwargs):
        self.modified_date = timezone.now()
        return super(ItemImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_date = timezone.now()
        self.save()

    class Meta:
        app_label = 'items'
        verbose_name = _('item image')
        verbose_name_plural = _('item images')


class ItemDocument(ChannelRelationship):
    """
    ItemDocument model
    """
    document = models.ForeignKey(
        'uploads.UploadedDocument',
        blank=True,
        null=True,
        verbose_name=_('document'),
        on_delete=models.DO_NOTHING)
    item = models.ForeignKey(
        'Item',
        models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_('item'))
    deleted = models.BooleanField(_("Deleted"), default=False)
    # Date fields
    created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Modified date'), auto_now=True)
    deleted_date = models.DateTimeField(
        _("Deleted date"), blank=True, null=True)

    def save(self, *args, **kwargs):
        self.modified_date = timezone.now()
        return super(ItemDocument, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_date = timezone.now()
        self.save()

    class Meta:
        app_label = 'items'
        verbose_name = _('item document')
        verbose_name_plural = _('item documents')
