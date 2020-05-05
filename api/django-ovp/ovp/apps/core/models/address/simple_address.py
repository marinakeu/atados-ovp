from django.db import models
from ovp.apps.channels.models.abstract import ChannelRelationship


class SimpleAddress(ChannelRelationship):
    street = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name='Logradouro'
    )

    # May contain letters as well
    number = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='Número'
    )
    neighbourhood = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Bairro'
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Cidade'
    )
    state = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Estado'
    )
    zipcode = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='CEP'
    )
    country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='País'
    )
    supplement = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Complemento'
    )

    @staticmethod
    def autocomplete_search_fields():
        return 'street', 'city',

    def __str__(self):
        params = {
            'street': self.street,
            'number': self.number,
            'neighbourhood': self.neighbourhood,
            'city': self.city
        }
        return "{street}, {number} - {neighbourhood} - {city}".format(**params)
