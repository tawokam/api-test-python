from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Lecture publique. Modification/suppression réservée à l'auteur"""
    message = "Vous n'etes pas l'auteur de cet objet."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.auteur == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """Lecture publique, écriture réservée aux admins (is_staff)."""
    message = "Action réservée aux administrateurs."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class IsModeratorOrOwner(permissions.BasePermission):
    """
    - Lecture : tout le monde
    - Ecriture : auteur ou un staff/moderator
    """
    message = "Réservé à l'auteur ou à un modérateur."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return obj.auteur == request.user

class CanWriteArticles(permissions.BasePermission):
    """Lecture publique, écriture réservée aux authors/moderators/staff."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return getattr(request.user, 'profile', Nome) and request.user.profile.role in ('author', 'moderator')