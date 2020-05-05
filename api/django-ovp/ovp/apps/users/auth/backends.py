from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from ovp.apps.channels.exceptions import NoChannelSupplied

UserModel = get_user_model()


class UserDeactivatedException(Exception):
    response = {
        'success': False,
        'error': {
            'name': 'UserDeactivated',
            'detail': 'This user is deactivated and can not login anymore.'
        }
    }

class ChannelBasedAuthentication(ModelBackend):
    def authenticate(
            self,
            request,
            username=None,
            password=None,
            channel=None,
            **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if channel is None:
            raise NoChannelSupplied()

        try:
            user = UserModel.objects.get(email__iexact=username.lower(), channel__slug=channel)
            user.LOGIN = True
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(
                    password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False.
        Instead of returning None, raise an exception if user is deactivated
        """
        is_active = getattr(user, 'is_active', None)
        if is_active == False:
            raise UserDeactivatedException
        return is_active or is_active is None
