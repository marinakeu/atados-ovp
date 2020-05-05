from functools import wraps

from dateutil.relativedelta import relativedelta

from django.utils import timezone

from ovp.apps.users.models import PasswordHistory

from ovp.apps.channels.cache import get_channel_setting


def expired_password(function):

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        representation = function(self, *args, **kwargs)
        request = self.context["request"]

        expiry_time = int(
            get_channel_setting(
                request.channel,
                "EXPIRE_PASSWORD_IN")[0])

        if expiry_time:
            representation["expired_password"] = False
            entry = PasswordHistory.objects.filter(
                user=request.user).order_by('-pk').first()

            if not entry:
                representation["expired_password"] = True
            else:
                delta = relativedelta(seconds=expiry_time)
                if timezone.now() - delta > entry.created_date:
                    representation["expired_password"] = True

        return representation

    return wrapper
