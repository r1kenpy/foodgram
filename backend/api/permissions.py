from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
)


class ReadOrIsAuthenticatedPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.method in SAFE_METHODS


class CurrentUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if type(obj) == type(user) and obj == user:
            return True or request.method in SAFE_METHODS
        return request.method in SAFE_METHODS
