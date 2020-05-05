from rest_framework import serializers

from ovp.apps.core.models import Skill
from ovp.apps.core.models import Cause


def skill_exist(v):  # pragma: no cover
    try:
        Skill.objects.get(id=v['id'])
    except Skill.DoesNotExist:
        raise serializers.ValidationError(
            {
                'id': "Skill with 'id' {} does not exist.".format(v['id'])
            }
        )


def cause_exist(v):  # pragma: no cover
    try:
        Cause.objects.get(id=v['id'])
    except Cause.DoesNotExist:
        raise serializers.ValidationError(
            {
                'id': "Cause with 'id' {} does not exist.".format(v['id'])
            }
        )
