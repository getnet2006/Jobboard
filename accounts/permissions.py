from rest_framework import permissions


class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "client"


class IsFreelancer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "freelancer"


class IsJobOwner(permissions.BasePermission):
    # This ensures only the job owner (client) can view/update/delete their job.
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user
