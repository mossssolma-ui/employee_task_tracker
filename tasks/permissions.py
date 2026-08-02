from rest_framework.permissions import SAFE_METHODS, IsAuthenticated


class IsOwner(IsAuthenticated):
    """Проверка, что юзер является владельцем задачи"""

    message = "Вы не являетесь владельцем этой задачи"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsTaskEmployee(IsAuthenticated):
    """Проверка, что юзер является исполнителем задачи"""

    message = "Вы не являетесь исполнителем этой задачи"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.employee == request.user
