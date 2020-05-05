from ovp.apps.core import validators
from ovp.apps.core.models import Availability

from ovp.apps.channels.serializers import ChannelRelationshipSerializer


class AvailabilitySerializer(ChannelRelationshipSerializer):
    def to_representation(self, instance):
        return {'weekday': instance.weekday, 'period': instance.period}

    def validate(self, data):
        if 'period_index' not in data:
            data['period_index'] = Availability.compose_period_index_for(
                data.get('weekday', 0),
                data.get('period', 0)
            )
        return super().validate(data)

    class Meta:
        fields = ['weekday', 'period']
        model = Availability
