from rest_framework import permissions
from rest_framework import exceptions

from ovp.apps.gallery.models import Gallery
from ovp.apps.projects.models import Project
from ovp.apps.core.models import Post

from ovp.apps.projects.permissions import (
    ProjectRetrieveOwnsOrIsOrganizationMember
)

from django.shortcuts import get_object_or_404
from django.db.models import Q


##############################
# Project Resource permissions
##############################

class GalleryEditAllowed(permissions.BasePermission):
    """
    Permission that allows an gallery owner
    to edit the gallery. Members of organization
    can edit the gallery if it is associated with
    a project or project.post.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if obj.owner == request.user:
                return True

        projects = list(
            Project.objects.filter(Q(galleries=obj) | Q(posts__gallery=obj))
        )
        if len(projects):
            perm = ProjectRetrieveOwnsOrIsOrganizationMember()
            failed = False
            for project in projects:
                if not perm.has_object_permission(request, view, project):
                    failed = True

            if failed:
                raise exceptions.PermissionDenied()  # 403
            else:
                return True

            raise exceptions.PermissionDenied()  # 403
        return False  # 401 #pragma: no cover
