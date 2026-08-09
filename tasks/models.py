from django.conf import settings
from django.db import models
from django.utils import timezone

from tasks.validators import (
    validate_deadline,
    validate_employee_is_active,
    validate_no_self_parent,
    validate_no_task_repeat,
    validate_owner_not_employee,
    validate_status,
    validate_title_length,
)


class Task(models.Model):
    """Модель задачи"""

    class TaskStatus(models.TextChoices):
        """Статусы задач"""

        CREATED = "created", "Создана"
        PROCESSING = "processing", "В работе"
        COMPLETED = "completed", "Завершена"
        CANCELLED = "cancelled", "Отменена"

    class TaskPriority(models.TextChoices):
        """Приоритеты задач"""

        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"
        VERY_HIGH = "very_high", "Очень высокий"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="employee_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Сотрудник",
        help_text="Выберите сотрудника, ответственного за выполнение задачи",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owner_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Кто создал задачу",
    )
    title = models.CharField(max_length=300, verbose_name="Наименование", help_text="Введите наименование задачи")
    description = models.TextField(blank=True, verbose_name="Описание задачи", help_text="Подробное описание задачи")
    parent_task = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="subtasks",
        blank=True,
        null=True,
        verbose_name="Связанная задача",
        help_text="Укажите связанную родительскую задачу",
    )
    deadline = models.DateField(
        verbose_name="Срок выполнения",
        help_text="Укажите дату дедлайна",
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.CREATED,
        verbose_name="Статус задачи",
        help_text="Текущий статус выполнения задачи",
    )
    priority = models.CharField(
        max_length=10,
        choices=TaskPriority.choices,
        default=TaskPriority.LOW,
        verbose_name="Приоритет задачи",
        help_text="Важность задачи",
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата завершения", help_text="Авто заполнение после завершения задачи"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def clean(self):
        """
        Валидация на уровне модели
        """
        validate_deadline(self)
        validate_title_length(self)
        validate_owner_not_employee(self)
        validate_no_self_parent(self)
        validate_employee_is_active(self)
        validate_status(self)
        validate_no_task_repeat(self)

    def save(self, *args, **kwargs):
        """Переопределям save для валидации"""

        if self.status == self.TaskStatus.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.TaskStatus.COMPLETED:
            self.completed_at = None

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-priority", "deadline"]
