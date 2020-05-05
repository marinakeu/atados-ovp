from ovp.apps.core import pagination
from django.utils import timezone

from ovp.apps.projects.models import Project
from ovp.apps.projects.serializers.project import (
    ProjectManageableRetrieveSerializer
)
from ovp.apps.ratings import models
from ovp.apps.ratings import serializers
from ovp.apps.ratings.permissions import UserCanRateRequest

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import decorators
from rest_framework import response

from ovp.apps.channels.viewsets.decorators import ChannelViewSet


@ChannelViewSet
class RatingRequestResourceViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    lookup_field = 'uuid'
    pagination_class = pagination.NoPagination

    @decorators.action(methods=["GET"], detail=False)
    def projects_with_unrated_users(self, request, *args, **kwargs):
        pks = models.RatingRequest.objects.filter(
            channel__slug=request.channel,
            deleted_date=None,
            rating=None,
            requested_user=self.request.user,
            content_type__model="user",
            initiator_type__model="project").values_list(
            "initiator_id",
            flat=True).distinct()
        projects = Project.objects.filter(
            channel__slug=request.channel, pk__in=pks)
        serializer = self.get_serializer(projects, many=True)
        return response.Response(serializer.data, status=200)

    @decorators.action(methods=["DELETE"], detail=True)
    def delete(self, request, *args, **kwargs):
        ctx = self.get_serializer_context()
        obj = self.get_object()
        obj.deleted_date = timezone.now()
        obj.save()
        return response.Response({"success": True}, status=200)

    @decorators.action(methods=["POST"], detail=True)
    def rate(self, request, *args, **kwargs):
        ctx = self.get_serializer_context()
        ctx['rating_request'] = self.get_object()

        # Owner
        request.data['owner'] = request.user.pk

        # Request
        request.data['request'] = ctx['rating_request'].pk

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context=ctx)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({"success": True}, status=200)

    def get_queryset(self, *args, **kwargs):
        qs = models.RatingRequest.objects.filter(
            channel__slug=self.request.channel,
            requested_user=self.request.user,
            deleted_date=None,
            rating=None)

        content_type = self.request.GET.get("object_type", None)
        if content_type in ["user", "project", "organization"]:
            qs = qs.filter(content_type__model=content_type)

        initiator_slug = self.request.GET.get("initiator_project_slug", None)
        if initiator_slug:
            pks = Project.objects.filter(
                slug=initiator_slug).values_list(
                "pk", flat=True)
            qs = qs.filter(
                initiator_type__model="project",
                initiator_id__in=pks)

        return qs

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'rate':
            return serializers.RatingCreateSerializer

        if self.action == 'projects_with_unrated_users':
            return ProjectManageableRetrieveSerializer

        return serializers.RatingRequestRetrieveSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = (permissions.IsAuthenticated, )

        if self.action == 'retrieve':
            self.permission_classes = (permissions.IsAuthenticated, )

        if self.action == 'rate':
            self.permission_classes = (
                permissions.IsAuthenticated, UserCanRateRequest)

        if self.action == 'delete':
            self.permission_classes = (
                permissions.IsAuthenticated, UserCanRateRequest)

        return super().get_permissions()
