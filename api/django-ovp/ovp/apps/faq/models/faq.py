from django.db import models
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextField

from ovp.apps.channels.models.abstract import ChannelRelationship


class Faq(ChannelRelationship):
    question = models.CharField(_('Question'), max_length=100)
    answer = RichTextField(
        verbose_name=_('Answer'),
        max_length=3000,
        default='')
    category = models.ForeignKey(
        'faq.FaqCategory',
        verbose_name=_('Category'),
        null=False,
        blank=True,
        default=0,
        on_delete=models.DO_NOTHING)
    language = models.CharField(
        _('Language'),
        null=True,
        blank=True,
        default=None,
        max_length=10)

    class Meta:
        app_label = 'faq'
        verbose_name = _('faq')
        verbose_name_plural = _('faq')
