import six
import sys
from social_django.strategy import DjangoStrategy
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError
from ovp.apps.users.models.profile import get_profile_model

User = get_user_model()
UserProfile = get_profile_model()


class OVPDjangoStrategy(DjangoStrategy):
    def get_kwargs(self, **kwargs):
        data = {"email": kwargs["email"]}

        get_kwargs = dict(data)
        create_kwargs = dict(data)

        # Get kwargs
        get_kwargs["channel__slug"] = self.request.channel

        # Create kwargs
        create_kwargs["object_channel"] = self.request.channel

        return get_kwargs, create_kwargs

    def create_user(self, *args, **kwargs):
        get_kwargs, create_kwargs = self.get_kwargs(**kwargs)

        try:
            user = super(
                OVPDjangoStrategy,
                self).create_user(
                *
                args,
                **create_kwargs)
            UserProfile.objects.create(
                user=user, object_channel=self.request.channel)
            return user
        except FieldError:
            # This happens because DjangoStorage is trying to .get the User
            # passing object_channel which is a write only field.
            # We try to fetch the user here instead
            exc_info = sys.exc_info()
            try:
                return User.objects.get(*args, **get_kwargs)
            except User.DoesNotExist:
                six.reraise(*exc_info)
