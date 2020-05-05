from ovp.apps.core import models
from ovp.apps.channels.serializers import ChannelRelationshipSerializer


class SimpleAddressSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.SimpleAddress
        fields = [
            'street',
            'number',
            'neighbourhood',
            'city',
            'state',
            'zipcode',
            'country',
            'supplement'
        ]
