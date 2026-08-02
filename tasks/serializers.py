from django.core.exceptions import ValidationError
from rest_framework import serializers

from tasks.models import Task
from tasks.services import is_task_overdue


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для модели задачи"""

    is_overdue = serializers.SerializerMethodField()

    employee_full_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_email = serializers.EmailField(source="employee.email", read_only=True)

    owner_full_name = serializers.CharField(source="owner.full_name", read_only=True)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "deadline",
            "status",
            "priority",
            "employee_id",
            "employee_full_name",
            "employee_email",
            "owner_id",
            "owner_full_name",
            "owner_email",
            "parent_task",
            "completed_at",
            "created_at",
            "updated_at",
            "is_overdue",
        ]
        read_only_fields = [
            "id",
            "owner_id",
            "created_at",
            "updated_at",
            "completed_at",
            "is_overdue",
            "employee_full_name",
            "employee_email",
            "owner_full_name",
            "owner_email",
        ]

    def get_is_overdue(self, obj):
        return is_task_overdue(obj)

    def validate(self, attrs):
        """
        Вызов валидации модели при создании и обновлении через API
        """
        if self.instance:
            instance = self.instance
            for attr, value in attrs.items():
                setattr(instance, attr, value)
        else:
            instance = Task(**attrs)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs
