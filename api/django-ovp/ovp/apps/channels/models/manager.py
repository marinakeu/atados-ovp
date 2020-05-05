from django.db import models
from ovp.apps.channels.models.mixins import ChannelCreatorMixin


class ChannelRelationshipManager(ChannelCreatorMixin, models.Manager):
    """
    All models that extend from ChannelRelationship must use this manager
    or another manager that extends from it.

    This manager overrides the .create() method
    so all objects created with .objects.create()
    get associated with channel.
    """

    def create(self, *args, **kwargs):
        self.check_direct_channel_association_kwargs(kwargs)
        object_channel, kwargs = self.pop_channel_from_kwargs(kwargs)

        # We don't use super().create here because the parent .create()
        # doesn't pass kwargs down to .save() method
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(
            force_insert=True,
            using=self.db,
            object_channel=object_channel
        )

        return obj
