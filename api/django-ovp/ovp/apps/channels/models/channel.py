from django.db import models
from django.utils.translation import ugettext_lazy as _


class Channel(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    slug = models.CharField(_('Slug'), max_length=100)
