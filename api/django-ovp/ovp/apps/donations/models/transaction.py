import uuid
from django.db import models
from ovp.apps.channels.models import ChannelRelationship


class Transaction(ChannelRelationship):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey('users.user', on_delete=models.CASCADE)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE)
    amount = models.IntegerField(blank=False, null=False)
    status = models.CharField(max_length=80)
    message = models.TextField()
    backend_transaction_id = models.CharField(
        max_length=80, blank=True, null=True)
    backend_transaction_number = models.CharField(
        max_length=80, blank=True, null=True)
    anonymous = models.BooleanField('Anonymous subscription', default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
