from rest_framework.permissions import BasePermission


class IsAdminOrIfAuthenticatedBorrowingPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action in ["create", "list", "retrieve"]:
            return request.user.is_authenticated
        elif view.action in ["update", "partial_update", "destroy"]:
            return request.user.is_staff
        else:
            return True
