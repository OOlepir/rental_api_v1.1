from rest_framework.permissions import BasePermission

class OnlyOwnerChangeStatus(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["PUT", "PATCH"]:
            status = request.data.get('status')
            if status and status != obj.status:
                return obj.property.owner == request.user
        return True
