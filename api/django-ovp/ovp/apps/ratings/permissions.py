from rest_framework import permissions


class UserCanRateRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.requested_user:
            return True
        return False
