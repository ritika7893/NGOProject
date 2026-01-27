from rest_framework import permissions
from .models import AllLog

class IsAdminRole(permissions.BasePermission):
    """
    Allow access only to authenticated admin users.
    """

    def has_permission(self, request, view):
        user = request.user

        # Must be authenticated
        if not user or not user.is_authenticated:
            return False

        try:
            alllog_user = AllLog.objects.get(id=user.id)
            return alllog_user.role == "admin"
        except AllLog.DoesNotExist:
            return False
