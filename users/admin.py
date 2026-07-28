from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Модель пользователя для админки"""

    list_display = ("id", "email", "position", "status", "is_active", "is_staff", "is_superuser", "date_of_employment")
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email",)
    ordering = ("is_active", "-date_of_employment")
    readonly_fields = ("date_joined", "last_login", "updated_at")

    fieldsets = (
        ("Изменить данные авторизации", {"fields": ("email", "password")}),
        (
            "Личная информация",
            {"fields": ("last_name", "first_name", "phone_number", "city", "avatar")},
        ),
        (
            "Рабочая информация",
            {"fields": ("position", "date_of_employment", "status")},
        ),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Дата регистрации/входа", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "position",
                    "phone_number",
                    "date_of_employment",
                ),
            },
        ),
    )
