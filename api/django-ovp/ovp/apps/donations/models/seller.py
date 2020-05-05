import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ovp.apps.channels.models import ChannelRelationship


class Seller(ChannelRelationship):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE)
    seller_id = models.CharField(max_length=80)
    backend = models.CharField(max_length=80)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'donations'
        verbose_name = _('seller')
        unique_together = (('organization', 'seller_id'), )
