from ovp.apps.channels.models import Channel

from ovp.apps.channels.exceptions import UnexpectedChannelAssociationError
from ovp.apps.channels.exceptions import NoChannelSupplied


class ChannelCreatorMixin(object):
    """
    This mixin is used by ChannelRelationshipManager and ChannelRelationship.

    It contains basic functionality to associate
    a object with a single channel.
    """

    def pop_channel_from_kwargs(self, kwargs):
        """
        Pop object_channel from kwargs,
        either from .save() or .manager.create()
        """
        channel = kwargs.pop("object_channel", None)

        if not channel:
            raise NoChannelSupplied()

        return channel, kwargs

    def pop_channel_as_object_from_kwargs(self, kwargs):
        channel, kwargs = self.pop_channel_from_kwargs(kwargs)
        channel = Channel.objects.get(slug=channel)

        return channel, kwargs

    def check_direct_channel_association_instance(self):
        """
        Check if it's not trying to directly associate a channel with the model
        with obj.channel = channel, obj.save().

        Use object_channel=channel_slug instead.
        """
        try:
            self.channel
            raise UnexpectedChannelAssociationError()
        except Channel.DoesNotExist:
            pass

        return True

    def check_direct_channel_association_kwargs(self, kwargs):
        """
        Check if it's not trying to directly associate
        a channel with the manager
        create method: .manager.create(channel=channel).

        Use object_channel=channel_slug instead.
        """
        if "channel" in kwargs:
            raise UnexpectedChannelAssociationError()

        return True
