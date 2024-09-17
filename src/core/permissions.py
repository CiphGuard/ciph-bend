from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Custom permission to only allow owner of an object to view or edit it.
    You need to add is_owner method to the model to use this permission.

    Example:
        In your model:
        def is_owner(self, user):
            return self.user == user
    """

    def has_object_permission(self, request, view, obj):
        return obj.is_owner(request.user)
