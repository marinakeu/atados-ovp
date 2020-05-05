from rest_framework import serializers

import re

from ovp.apps.users.models import User

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError
from django.core import validators

from django.utils.translation import ugettext_lazy as _


class InviteEmailValidator():
    def __call__(self, email):
        try:
            validate_email(email)
        except ValidationError as e:
            # we let serializers.EmailField validation handle invalid emails
            return True

        try:
            User.objects.get(email__iexact=email, channel__slug=self.channel)
        except User.DoesNotExist:
            raise serializers.ValidationError("This user is not valid.")

    def set_context(self, serializer):
        self.channel = serializer.context['request'].channel


error_messages = {
    'invalid': ("Invalid CNPJ number."),
    'digits_only': ("This field requires only numbers."),
    'max_digits': (
        "This field requires exactly 14 digits "
        "in the format XXXXXXXXXXXXXX without '. / -'"
    ),
}


def DV_maker(v):
    if v >= 2:
        return 11 - v
    return 0


def validate_CNPJ(value):
    """
    Value can be either a string in the format XX.XXX.XXX/XXXX-XX or a
    group of 14 characters.
    :type value: object
    """
    if value is None or len(value) == 0:
        return None

    value = str(value)
    if not value.isdigit():
        value = re.sub(r"[-/\.]", "", value)
    orig_value = value[:]
    try:
        int(value)
    except ValueError:
        raise ValidationError(error_messages['digits_only'])
    if len(value) > 14:
        raise ValidationError(error_messages['max_digits'])
    orig_dv = value[-2:]

    new_1dv = sum(
        [
            i * int(value[idx]) for idx,
            i in enumerate(list(range(5, 1, -1)) + list(range(9, 1, -1)))
        ]
    )
    new_1dv = DV_maker(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum(
        [
            i * int(value[idx]) for idx,
            i in enumerate(list(range(6, 1, -1)) + list(range(9, 1, -1)))
        ]
    )
    new_2dv = DV_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise ValidationError(error_messages['invalid'])

    return orig_value


def format_CNPJ(value):
    if value is None or len(value) == 0:
        return None
    value = re.sub(r"[-/\.]", "", value)
    return '{}.{}.{}/{}-{}'.format(value[0:2],
                                   value[2:5],
                                   value[5:8],
                                   value[8:12],
                                   value[12:])
