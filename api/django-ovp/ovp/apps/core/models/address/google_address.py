from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.models.abstract import ChannelRelationship
from ovp.apps.channels.cache import get_channel_setting

import os
import requests
import vcr


class AddressComponentType(ChannelRelationship):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AddressComponent(ChannelRelationship):
    long_name = models.CharField(max_length=400)
    short_name = models.CharField(max_length=400)
    types = models.ManyToManyField(AddressComponentType)

    def __str__(self):
        return self.long_name


class GoogleRegion(ChannelRelationship):
    region_name = models.CharField(max_length=400)
    filter_by = models.CharField(max_length=400)


class GoogleAddress(ChannelRelationship):
    typed_address = models.CharField(
        _("Typed address"),
        max_length=400,
        blank=True,
        null=True
    )
    typed_address2 = models.CharField(
        _("Typed address 2"),
        max_length=400,
        blank=True,
        null=True
    )
    address_line = models.CharField(
        _("Address line"),
        max_length=400,
        blank=True,
        null=True
    )
    city_state = models.CharField(
        _("City/state"),
        max_length=400,
        blank=True,
        null=True
    )
    lat = models.FloatField(_('Latitude'), blank=True, null=True)
    lng = models.FloatField(_('Longitude'), blank=True, null=True)
    address_components = models.ManyToManyField(AddressComponent)

    @staticmethod
    def autocomplete_search_fields():
        return 'typed_address',

    def get_state(self):
        state = self.address_components.filter(
            types__name='administrative_area_level_1'
        )

        if state.count():
            return state[0].short_name
        return ""

    def get_city_state(self):
        state = self.address_components.filter(
            types__name='administrative_area_level_1'
        )
        county = self.address_components.filter(
            types__name='administrative_area_level_2'
        )
        sublocality = self.address_components.filter(types__name='sublocality')
        locality = self.address_components.filter(types__name='locality')

        s = u""
        if locality.count():
            s += u"{}, ".format(locality[0].long_name)
        elif county.count():
            s += u"{}, ".format(county[0].long_name)
        elif sublocality.count():
            s += u"{}, ".format(sublocality[0].long_name)

        if state.count():
            s += state[0].short_name

        return s

    def address_dict(self):
        # Components types for address
        address = {
            'route': '',
            'sublocality_level_1': '',
            'administrative_area_level_2': '',
            'administrative_area_level_1': '',
            'country': '',
            'street_number': '',
            'postal_code': ''
        }

        # Fill address dict
        for component in self.address_components.all():
            for component_type in component.types.all():
                if component_type.name in address:
                    address[component_type.name] = {
                        'short_name': component.short_name,
                        'long_name': component.long_name
                    }

        return address

    def get_address(self):
        address = self.address_dict()

        # Build address string
        string_address = ''
        if 'route' in address and isinstance(address['route'], dict):
            string_address += '{}, '.format(address['route']['long_name'])
        if 'route' in address and isinstance(address['street_number'], dict):
            string_address += '{}, '.format(
                address['street_number']['long_name']
            )
        if ('sublocality_level_1' in address and
                isinstance(address['sublocality_level_1'], dict)):
            string_address += '{}, '.format(
                address['sublocality_level_1']['long_name']
            )
        if ('administrative_area_level_2' in address and
                isinstance(address['administrative_area_level_2'], dict)):
            string_address += '{}, '.format(
                address['administrative_area_level_2']['long_name']
            )
        if ('administrative_area_level_1' in address and
                isinstance(address['administrative_area_level_1'], dict)):
            string_address += '{}, '.format(
                address['administrative_area_level_1']['short_name']
            )
        if 'country' in address and isinstance(address['country'], dict):
            string_address += '{}, '.format(address['country']['long_name'])

        string_address = string_address.strip().strip(',')

        return string_address

    def get_country_code(self):
        try:
            return self.address_components.filter(
                types__name='country'
            ).first().short_name.lower()
        except AttributeError:
            return None

    def __str__(self):
        if self.address_line:
            return self.address_line
        elif self.typed_address:
            return self.typed_address
        return ""

    class Meta:
        app_label = 'core'
        verbose_name = _('google address')
        verbose_name_plural = _('google addresses')


@receiver(post_save, sender=GoogleAddress)
def update_address(sender, instance, **kwargs):
    if kwargs.get('raw', False):  # pragma: no cover
        return None

    maps_language = get_channel_setting(
        instance.channel.slug,
        "MAPS_API_LANGUAGE"
    )[0]

    addressline = instance.typed_address
    endpoint = 'https://maps.googleapis.com/maps/api/geocode/json'
    url = '{}?language={}&address={}'.format(
        endpoint,
        maps_language,
        addressline
    )

    key = os.environ.get('GOOGLE_MAPS_KEY', None)
    if key:  # pragma: no cover
        url = '{}&key={}'.format(url, key)

    with vcr.use_cassette("/tmp/google-address", record_mode="new_episodes"):
        r = requests.get(url)
    data = r.json()

    # Iterate through address components
    instance.address_components.clear()
    if len(data['results']) > 0:
        for component in data['results'][0]['address_components']:
            # TODO: Do not work only with first result
            # Look for component with same name and type
            ac = AddressComponent.objects.annotate(count=Count('types'))
            ac = ac.filter(
                long_name=component['long_name'],
                short_name=component['short_name']
            )
            for component_type in component['types']:
                ac = ac.filter(types__name=component_type)
            ac = ac.filter(count=len(component['types']))

            if not ac.count():
                # Component not found, creating
                ac = AddressComponent(
                    long_name=component['long_name'],
                    short_name=component['short_name']
                )
                ac.save(object_channel=instance.channel.slug)
            else:
                ac = ac.first()
                ac.types.clear()
                ac.save()

            # Add types for component
            for ctype in component['types']:
                try:
                    at = AddressComponentType.objects.get(name=ctype)
                except ObjectDoesNotExist:
                    at = AddressComponentType(name=ctype)
                    at.save(object_channel=instance.channel.slug)
                ac.types.add(at)

            instance.address_components.add(ac)

        try:
            if data['results'][0]['geometry']:
                GoogleAddress.objects.filter(pk=instance.pk).update(
                    lat=data['results'][0]['geometry']['location']['lat'],
                    lng=data['results'][0]['geometry']['location']['lng']
                )
        except Exception:  # pragma: no cover
            pass

        # Using update to avoid post_save signal
        GoogleAddress.objects.filter(pk=instance.pk).update(
            address_line=instance.get_address(),
            city_state=instance.get_city_state()
        )
