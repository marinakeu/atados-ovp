from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import Http404

from ovp.apps.core.serializers import EmptySerializer

from ovp.apps.channels.viewsets.decorators import ChannelViewSet
from ovp.apps.channels.cache import get_channel_setting
from ovp.apps.channels.content_flow import CFM

from ovp.apps.projects.serializers import apply as serializers
from ovp.apps.projects import models
from ovp.apps.projects.permissions import ProjectApplyPermission

from rest_framework import decorators
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema


@ChannelViewSet
class ApplyResourceViewSet(viewsets.GenericViewSet):
    """
    ApplyResourceViewSet resource endpoint
    """

    ##################
    # ViewSet routes #
    ##################
    def list(self, request, *arg, **kwargs):
        """ Retrieve a list of applies for a project. """
        applies = self.get_queryset(**kwargs)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            applies,
            many=True,
            context=self.get_serializer_context()
        )

        return response.Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """ Update an apply status. """
        instance = self.get_queryset(**kwargs).get(pk=kwargs['pk'])
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # pragma: no cover
        if getattr(instance, '_prefetched_objects_cache', None):
            instance = self.get_object()
            serializer = self.get_serializer(instance)

        return response.Response(serializer.data)

    @swagger_auto_schema(method="POST", responses={200: 'OK'})
    @decorators.action(['POST'], detail=False)
    def apply(self, request, *args, **kwargs):
        """ Apply authenticated user for project. """
        data = request.data
        data.pop('user', None)

        project = self.get_project_object(**kwargs)

        data['project'] = project.id

        if request.user.is_authenticated:
            user = request.user
            data['username'] = user.name
            data['email'] = user.email
            data['phone'] = user.phone
            data['user'] = user.id

        try:
            existing_apply = self.get_queryset(**kwargs)
            existing_apply = existing_apply.get(
                email=data['email'],
                status='unapplied'
            )
            existing_apply.status = "applied"
            existing_apply.role_id = data['role'] if 'role' in data else None
            existing_apply.save()
            obj = existing_apply
        except ObjectDoesNotExist:
            apply_sr_class = self.get_serializer_class()
            apply_sr = apply_sr_class(
                data=data,
                context=self.get_serializer_context()
            )
            apply_sr.is_valid(raise_exception=True)
            obj = apply_sr.save()

        return response.Response(
            serializers.ApplyRetrieveSerializer(
                obj,
                context=self.get_serializer_context()
            ).data,
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(method="POST", responses={200: 'OK'})
    @decorators.action(['POST'], detail=False)
    def unapply(self, request, *args, **kwargs):
        """ Unapply authenticated user for project. """
        project = self.get_project_object(**kwargs)
        user = request.user

        try:
            existing_apply = self.get_queryset(**kwargs)
            existing_apply = existing_apply.exclude(
                status="unapplied"
            ).get(email=user.email)
            existing_apply.status = "unapplied"
            existing_apply.save()
        except ObjectDoesNotExist:
            return response.Response(
                {'detail': 'This is user is not applied to this project.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response.Response(
            {'detail': 'Successfully unapplied.'},
            status=status.HTTP_200_OK
        )

    ###################
    # ViewSet methods #
    ###################
    def get_queryset(self, *args, **kwargs):
        project = self.get_project_object(**kwargs)
        return models.Apply.objects.filter(project=project)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ApplyRetrieveSerializer

        if self.action == 'partial_update':
            return serializers.ApplyUpdateSerializer

        if self.action == 'apply':
            return serializers.ApplyCreateSerializer

        if self.action == 'unapply':
            return EmptySerializer

    def get_permissions(self):
        request = self.get_serializer_context()['request']

        if self.action in ['list', 'partial_update']:
            self.permission_classes = (
                permissions.IsAuthenticated,
                ProjectApplyPermission
            )

        if self.action == 'apply':
            channel_settings = get_channel_setting(
                request.channel,
                "UNAUTHENTICATED_APPLY"
            )
            if int(channel_settings[0]):
                self.permission_classes = ()
            else:
                self.permission_classes = (permissions.IsAuthenticated, )

        if self.action == 'unapply':
            self.permission_classes = (permissions.IsAuthenticated, )

        return super().get_permissions()

    def get_project_object(self, *args, **kwargs):
        slug = kwargs.get('project_slug')
        qs = CFM.filter_queryset(
            self.request.channel,
            models.Project.objects.all(),
            distinct=True
        )
        return get_object_or_404(qs, slug=slug)
