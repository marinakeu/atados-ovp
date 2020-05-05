from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.core.models import GoogleAddress, SimpleAddress

from django_extensions.admin import ForeignKeyAutocompleteAdmin


class GoogleAddressAdmin(ChannelModelAdmin, ForeignKeyAutocompleteAdmin):

    fields = [
        'id',
        'typed_address',
        'typed_address2'
    ]

    list_display = [
        'id', 'typed_address', 'typed_address2'
    ]

    search_fields = ['typed_address', 'typed_address2', 'address_line']

    readonly_fields = ['id']


admin_site.register(GoogleAddress, GoogleAddressAdmin)


class SimpleAddressAdmin(ChannelModelAdmin):

    fields = [
        'id',
        'zipcode',
        'street',
        'number',
        'supplement',
        'neighbourhood',
        'city',
        'state'
    ]

    list_display = ['id', 'street', 'city']
    search_fields = ['street', 'city']
    readonly_fields = ['id']


admin_site.register(SimpleAddress, SimpleAddressAdmin)
