from django.contrib import admin

from tasks.models import Task
from tasks.services import is_task_overdue


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Админка для управления задачами"""

    list_display = (
        "id",
        "title",
        "status",
        "priority",
        "employee",
        "owner",
        "parent_task",
        "deadline",
        "is_overdue",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "employee",
        "owner",
        "deadline",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "employee__email",
        "employee__full_name",
        "owner__email",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "completed_at",
    )

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "description",
                    "status",
                    "priority",
                )
            },
        ),
        (
            "Исполнители",
            {
                "fields": (
                    "employee",
                    "owner",
                )
            },
        ),
        (
            "Зависимости и сроки",
            {
                "fields": (
                    "parent_task",
                    "deadline",
                )
            },
        ),
        (
            "Системная информация",
            {
                "fields": (
                    "id",
                    "created_at",
                    "updated_at",
                    "completed_at",
                ),
            },
        ),
    )
    ordering = ("-created_at",)

    def is_overdue(self, obj):
        """Отображает, просрочена ли задача"""
        return is_task_overdue(obj)

    is_overdue.boolean = True
    is_overdue.short_description = "Просрочена"
