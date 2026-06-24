"""
Custom Permissions - Role Based Access Control
"""

from rest_framework.permissions import BasePermission
from .models import User


class IsAdministrador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.ADMINISTRADOR


class IsMedico(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.MEDICO, User.ADMINISTRADOR]


class IsAnalista(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.ANALISTA, User.ADMINISTRADOR]


class IsAdminOrAnalista(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.ADMINISTRADOR, User.ANALISTA
        ]


class IsAuthenticatedAnyRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
