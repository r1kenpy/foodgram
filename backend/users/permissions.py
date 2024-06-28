from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOrChangeUserPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.method in SAFE_METHODS
