from ovp.apps.projects import models
from ovp.apps.channels.serializers import ChannelRelationshipSerializer


class WorkSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.Work
        fields = [
            'weekly_hours',
            'description',
            'project',
            'can_be_done_remotely'
        ]
        extra_kwargs = {'project': {'write_only': True}}
