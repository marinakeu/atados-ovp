from ovp.apps.core import models
from ovp.apps.channels.serializers import ChannelRelationshipSerializer


class GoogleAddressSerializer(ChannelRelationshipSerializer):
    class Meta:
        model = models.GoogleAddress
        fields = [
            'typed_address',
            'typed_address2',
            'address_line',
            'city_state'
        ]
        read_only_fields = ['address_line']


class GoogleAddressLatLngSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.GoogleAddress
        fields = [
            'typed_address',
            'typed_address2',
            'address_line',
            'city_state',
            'lat',
            'lng'
        ]
        read_only_fields = ['address_line', 'city_state']


class GoogleAddressCityStateSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.GoogleAddress
        fields = ['city_state']


class GoogleAddressShortSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.GoogleAddress
        fields = ['lat', 'lng']
        read_only_fields = ['lat', 'lng']
