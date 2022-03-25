from rest_framework.permissions import SAFE_METHODS, BasePermission
from reviews.models import MODERATOR


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает доступ только для администратора или только для чтения.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin()
        )


class IsAdmin(BasePermission):
    """
    Разрешает доступ только для администратора.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsAuthorOrReadOnlyOrModeratorOrAdmin(BasePermission):
    """
    Разрешает доступ только автору объекта, модератору, администратору
    или только для чтения.
    """
    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin()
            or request.user.is_authenticated and request.user.role == MODERATOR
        )
