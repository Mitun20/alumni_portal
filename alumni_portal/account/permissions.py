from rest_framework.permissions import BasePermission

class IsAlumniManagerOrAdministrator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.groups.filter(name='Alumni_Manager').exists() or 
             request.user.groups.filter(name='Administrator').exists())
        )

class IsAlumni(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Alumni').exists()

class IsFaculty(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Faculty').exists()

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Student').exists()
