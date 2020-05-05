from django.db import models
from ovp.apps.channels.models import ChannelRelationship


class PasswordHistory(ChannelRelationship, models.Model):
    hashed_password = models.CharField(max_length=300)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
