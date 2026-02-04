from rest_framework import permissions
from .models import AllLog, DistrictAdmin, RegionAdmin

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

class IsAdminOrDistrictAdminSelf(permissions.BasePermission):
  
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        try:
            alllog_user = AllLog.objects.get(unique_id=user.unique_id)
        except AllLog.DoesNotExist:
            return False

        if alllog_user.role == "admin":
            return True

        if alllog_user.role == "district-admin":
            return DistrictAdmin.objects.filter(
                district_admin_id=alllog_user.unique_id
            ).exists()

    
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        try:
            alllog_user = AllLog.objects.get(unique_id=user.unique_id)
        except AllLog.DoesNotExist:
            return False

        if alllog_user.role == "admin":
            return True
        return alllog_user.role == "district-admin" and obj.district_admin_id == alllog_user.unique_id


class IsAdminOrSelfUser(permissions.BasePermission):
  

    def has_permission(self, request, view):
        # Allow access to authenticated users; object-level checked later
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        try:
            alllog_user = AllLog.objects.get(unique_id=user.unique_id)
        except AllLog.DoesNotExist:
            return False

        if alllog_user.role == "admin":
            return True

        role_field_map = {
            "district-admin": "district_admin_id",
            "member": "member_id",
        }

        field_name = role_field_map.get(alllog_user.role)
        if not field_name:
            return False

        return getattr(obj, field_name, None) == alllog_user.unique_id
class IsDistrictAdmin(permissions.BasePermission):
    """
    Allows access only to DistrictAdmin users
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Role check
        if user.role != "district-admin":
            return False

        # Ensure linked DistrictAdmin exists
        return DistrictAdmin.objects.filter(
            district_admin_id=user.unique_id
        ).exists()
    

class IsAdminOrRegionAdminSelf(permissions.BasePermission):
  
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        try:
            alllog_user = AllLog.objects.get(unique_id=user.unique_id)
        except AllLog.DoesNotExist:
            return False

        if alllog_user.role == "admin":
            return True

        if alllog_user.role == "region-admin":
            return RegionAdmin.objects.filter(
                region_admin_id=alllog_user.unique_id
            ).exists()

    
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        try:
            alllog_user = AllLog.objects.get(unique_id=user.unique_id)
        except AllLog.DoesNotExist:
            return False

        if alllog_user.role == "admin":
            return True
        return alllog_user.role == "region-admin" and obj.region_admin_id == alllog_user.unique_id

class IsAdminOrDistrictOrRegionAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        try:
            alllog_user = AllLog.objects.get(unique_id=user.unique_id)
        except AllLog.DoesNotExist:
            return False

        # Admin has full access
        if alllog_user.role == "admin":
            return True

        # District Admin
        if alllog_user.role == "district-admin":
            return DistrictAdmin.objects.filter(
                district_admin_id=alllog_user.unique_id
            ).exists()

        # Region Admin
        if alllog_user.role == "region-admin":
            return RegionAdmin.objects.filter(
                region_admin_id=alllog_user.unique_id
            ).exists()

        return False

    def has_object_permission(self, request, view, obj):
        try:
            alllog_user = AllLog.objects.get(unique_id=request.user.unique_id)
        except AllLog.DoesNotExist:
            return False

        if alllog_user.role == "admin":
            return True

        if alllog_user.role == "district-admin":
            return getattr(obj, "district_admin_id", None) == alllog_user.unique_id

        if alllog_user.role == "region-admin":
            return getattr(obj, "region_admin_id", None) == alllog_user.unique_id

        return False