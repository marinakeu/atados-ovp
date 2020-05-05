import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from django_resized import ResizedImageField

from ovp.apps.channels.models.abstract import ChannelRelationship


@deconstructible
class ImageName(object):
    def __init__(self, sub_path=""):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (instance.uuid, ext)
        return 'user-uploaded/images%s/%s' % (self.path, filename)


image = ImageName()
image_small = ImageName("-small")
image_medium = ImageName("-medium")
image_large = ImageName("-large")


class UploadedImage(ChannelRelationship):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=None,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING
    )
    image = models.ImageField(
        _('Image 350x260'),
        upload_to=image,
        max_length=300
    )
    image_small = ResizedImageField(
        size=[350, 260],
        upload_to=image_small,
        blank=True,
        null=True,
        default=None,
        quality=90,
        max_length=300
    )
    image_medium = ResizedImageField(
        size=[420, 312],
        upload_to=image_medium,
        blank=True,
        null=True,
        default=None,
        quality=90,
        max_length=300
    )
    image_large = ResizedImageField(
        size=[1260, 936],
        upload_to=image_large,
        blank=True,
        null=True,
        default=None,
        quality=90,
        max_length=300
    )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    uuid = models.CharField(
        'UUID',
        max_length=36,
        default=None,
        null=False,
        blank=True
    )
    absolute = models.BooleanField('Absolute', default=False)
    name = models.CharField(
        _('Name'),
        max_length=64,
        default=None,
        null=True,
        blank=True
    )

    class Meta:
        app_label = 'uploads'
        verbose_name = _('uploaded image')
        verbose_name_plural = _('uploaded images')

    def __str__(self):
        return self.uuid

    @staticmethod
    def autocomplete_search_fields():
        return 'name',

    def save(self, *args, **kwargs):
        if not self.pk:
            self.uuid = str(uuid.uuid4())
        # If _committed == False, it means the image is not uploaded to s3 yet
        # (will be uploaded on super.save()).
        # This means the image is being updated
        # So we update other images accordingly
        if not self.image._committed:
            #  ._file because we need the InMemoryUploadedFile instance
            self.image_small = self.image._file
            self.image_medium = self.image._file
            self.image_large = self.image._file

        self.modified_date = timezone.now()
        return super().save(*args, **kwargs)


@deconstructible
class DocumentName(object):

    def __init__(self, sub_path=""):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (instance.uuid, ext)
        return 'user-uploaded/documents%s/%s' % (self.path, filename)


document = DocumentName()


class UploadedDocument(ChannelRelationship):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=None,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING
    )
    document = models.FileField(upload_to=document)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    uuid = models.CharField(
        'UUID',
        max_length=36,
        default=None,
        null=False,
        blank=True
    )
    name = models.CharField(
        _('Name'),
        max_length=64,
        default=None,
        null=True,
        blank=True
    )
    extension = models.CharField(
        _('Extension'),
        blank=True,
        null=True,
        max_length=5
    )
    size = models.IntegerField(_('Size'), blank=True, null=True, default=0)

    class Meta:
        app_label = 'uploads'
        verbose_name = _('uploaded document')
        verbose_name_plural = _('uploaded documents')

    def __str__(self):
        return self.uuid

    def save(self, *args, **kwargs):
        if not self.pk:
            self.uuid = str(uuid.uuid4())

        if not self.document._committed:
            self.extension = self.document.name.split('.')[-1]
            self.size = self.document.size

        self.modified_date = timezone.now()
        return super().save(*args, **kwargs)
