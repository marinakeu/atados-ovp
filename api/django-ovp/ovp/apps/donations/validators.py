from rest_framework import serializers
from ovp.apps.organizations.models import Organization


def organization_accepts_donations(organization_pk):
    try:
        Organization.objects.get(id=organization_pk, allow_donations=True)
    except Organization.DoesNotExist:
        raise serializers.ValidationError(
            {'organization_id': "Organization with 'id' {} and 'allow_donations' True does not exist.".format(organization_pk)})
