# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission


class EnsureAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsResearcher(BasePermission):
    """
    Allows access only to Customer.
    """
    def has_permission(self, request, view):
        return bool(request.user.role == request.user.RESEARCHER)

class IsCustomer(BasePermission):
    """
    Allows access only to Customer.
    """
    def has_permission(self, request, view):
        return bool(request.user.role == request.user.CUSTOMER)


class IsTriager(BasePermission):
    """
    Allows access only to Triager.
    """
    def has_permission(self, request, view):
        return bool(request.user.role == request.user.TRIAGER)





