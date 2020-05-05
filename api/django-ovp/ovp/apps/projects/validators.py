from ovp.apps.projects.models import Category

from rest_framework import serializers


def category_exist(v):  # pragma: no cover
    try:
        Category.objects.get(id=v['id'])
    except Category.DoesNotExist:
        raise serializers.ValidationError(
            {
                'id': "Category with 'id' {} does not exist.".format(v['id'])
            }
        )
