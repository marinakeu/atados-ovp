from django.contrib.auth.hashers import get_hasher

from ovp.apps.users.models import PasswordHistory, PasswordRecoveryToken

from ovp.apps.channels.cache import get_channel_setting

from rest_framework import serializers


class BasePasswordReuse(object):
    def set_context(self, serializer):
        self.request = serializer.context["request"]

    def check(self, user, password):
        amount = int(
            get_channel_setting(
                user.channel.slug,
                "CANT_REUSE_LAST_PASSWORDS")[0])

        if amount:
            history = PasswordHistory.objects.filter(
                user=user).order_by('-id')[:amount]

            for item in history:
                algorithm = item.hashed_password.split("$")[0]
                hasher = get_hasher(algorithm=algorithm)
                matches = hasher.verify(password, item.hashed_password)

                if matches:
                    raise serializers.ValidationError(
                        "You cannot reuse the last {} "
                        "used passwords.".format(amount)
                    )


class PasswordReuse(BasePasswordReuse):
    def __call__(self, password):
        if self.request.user.is_authenticated:
            super().check(self.request.user, password)


class PasswordReuseInRecovery(BasePasswordReuse):
    def __call__(self, password):
        token = PasswordRecoveryToken.objects.get(
            token=self.request.data.get("token", None))
        super().check(token.user, password)
