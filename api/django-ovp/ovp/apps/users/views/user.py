from django.db.models import Q
from ovp.apps.users import serializers
from ovp.apps.users import models
from ovp.apps.users import emails

from ovp.apps.projects.models import Apply

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from rest_framework import decorators
from rest_framework import mixins
from rest_framework import response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema


@ChannelViewSet
class UserResourceViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    UserResourceViewSet resource endpoint
    """
    queryset = models.User.objects.filter(is_active=True)
    lookup_field = 'slug'
    # default is [^/.]+ - here we're allowing dots in the url slug field
    lookup_value_regex = '[^/]+'

    def create(self, *args, **kwargs):
        """ Create an user. """
        return super(UserResourceViewSet, self).create(*args, **kwargs)

    def current_user_get(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.get_serializer(
            queryset, context=self.get_serializer_context())
        return response.Response(serializer.data)

    def current_user_patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(serializer.data)

    @decorators.action(url_path="current-user", detail=False, methods=['GET', 'PATCH'])
    def current_user(self, request, *args, **kwargs):
        """ Retrieve and update current user. """
        if request.method == 'GET':
            return self.current_user_get(request, *args, **kwargs)
        if request.method == 'PATCH':
            return self.current_user_patch(request, *args, **kwargs)

    @decorators.action(url_path="deactivate-account", detail=False, methods=['POST'])
    def deactivate_account(self, request, *args, **kwargs):
        """ Deactivate user account """
        user = request.user

        (Apply.objects
             .filter(user=user, status__in=['applied', 'confirmed-volunteer'])
             .update(status='unapplied-by-deactivation'))

        user.is_active = False
        user.save()
        return response.Response({'success': True})

    def get_object(self):
        request = self.get_serializer_context()['request']
        if self.action == 'current_user':
            return self.get_queryset().get(pk=request.user.pk)

        # Shouldn't really be called for current implementation
        # but here as fail-safe for future updates
        return super().get_object()  # pragma: no cover

    # We need to override get_permissions and get_serializer_class to work
    # with multiple serializers and permissions
    def get_permissions(self):
        request = self.get_serializer_context()['request']
        if self.action == 'create':
            self.permission_classes = []
        elif self.action in ['current_user', 'deactivate_account']:
            self.permission_classes = [permissions.IsAuthenticated, ]

        return super().get_permissions()

    def get_serializer_class(self):
        request = self.get_serializer_context()['request']

        if self.action == 'create':
            return serializers.UserCreateSerializer

        if self.action == 'current_user':
            if request.method == "GET":
                return serializers.CurrentUserSerializer
            elif request.method in ["PUT", "PATCH"]:
                return serializers.UserUpdateSerializer


@ChannelViewSet
class PublicUserResourceViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    """
    PublicUserResourceViewSet resource endpoint
    """
    serializer_class = serializers.LongUserPublicRetrieveSerializer
    lookup_field = 'slug'
    # default is [^/.]+ - here we're allowing dots in the url slug field
    lookup_value_regex = '[^/]+'
    email = ''
    locale = ''

    def get_queryset(self, *args, **kwargs):
        q = Q(public=True, is_active=True)

        if self.request.user.is_authenticated:
            q = q | Q(pk=self.request.user.pk)

        return models.User.objects.filter(q)

    def retrieve(self, *args, **kwargs):
        """ Retrieve an user profile. """
        return super().retrieve(*args, **kwargs)

    def mailing(self, async_mail=None):
        return emails.UserMail(self, async_mail)

    @swagger_auto_schema(auto_schema=None)
    @action(methods=['post'], detail=True, url_path='send-message')
    def send_message(self, request, slug, pk=None):
        """ This route is deprecated """
        self.email = self.get_queryset().get(slug=slug)
        context = {
            'message': request.data.get('message', None),
            'from_name': request.user.name,
            'from_email': request.user.email
        }

        self.mailing().sendMessageToAnotherVolunteer(context)
        return response.Response(True)
