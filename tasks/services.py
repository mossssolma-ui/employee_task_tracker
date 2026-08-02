from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from tasks.models import Task
from users.models import CustomUser


def is_task_overdue(task) -> bool:
    """Проверка, на просроченность задачи"""
    if task.status in [Task.TaskStatus.COMPLETED, Task.TaskStatus.CANCELLED]:
        return False
    return task.deadline < timezone.now().date()


def get_overdue_tasks() -> QuerySet[Task]:
    """Получает все просроченные задачи"""
    return Task.objects.filter(deadline__lt=timezone.now().date()).exclude(
        status__in=[Task.TaskStatus.COMPLETED, Task.TaskStatus.CANCELLED]
    )


def get_busy_employees() -> QuerySet[CustomUser]:
    """
    Получает список активных сотрудников, отсортированных по количеству активных задач.
    """
    return (
        CustomUser.objects.filter(is_active=True, status=CustomUser.EmployeeStatus.ACTIVE)
        .annotate(
            active_tasks_count=Count("employee_tasks", filter=Q(employee_tasks__status=Task.TaskStatus.PROCESSING))
        )
        .filter(active_tasks_count__gt=0)
        .order_by("-active_tasks_count")
    )


def get_important_tasks() -> QuerySet[Task]:
    """
    Запрашивает из БД задачи, которые не взяты в работу,
    но от которых зависят другие задачи, взятые в работу.
    """
    important_tasks = Task.objects.filter(
        status=Task.TaskStatus.CREATED, subtasks__status=Task.TaskStatus.PROCESSING
    ).distinct()
    return important_tasks


def get_potential_employees_for_important_task(important_tasks) -> list:
    """
    Реализует поиск по сотрудникам, которые могут взять такие задачи:
    - наименее загруженный сотрудник
    - Или сотрудник, выполняющий родительскую задачу,
    если ему назначено максимум на 2 задачи больше, чем у наименее загруженного сотрудника.
    Возвращает список объектов в формате: {Важная задача, Срок, [ФИО сотрудника]}
    """
    if not important_tasks.exists():
        return []

    all_active_employees = CustomUser.objects.filter(is_active=True, status=CustomUser.EmployeeStatus.ACTIVE).annotate(
        active_tasks_count=Count("employee_tasks", filter=Q(employee_tasks__status=Task.TaskStatus.PROCESSING))
    )

    if not all_active_employees.exists():
        return []

    employees = all_active_employees.order_by("active_tasks_count").first()
    min_tasks = employees.active_tasks_count
    max_allowed = min_tasks + 2

    result = []
    for task in important_tasks:
        subtask_employees_id = [
            subtask.employee_id
            for subtask in task.subtasks.all()
            if subtask.employee_id and subtask.employee.is_active
        ]

        candidates = all_active_employees.filter(
            Q(active_tasks_count=min_tasks) | Q(id__in=subtask_employees_id, active_tasks_count__lte=max_allowed)
        ).distinct()

        candidate_names = [employee.full_name if employee.full_name else employee.email for employee in candidates]

        result.append(
            {
                "task": task.title,
                "deadline": task.deadline,
                "candidates": candidate_names,
            }
        )

    return result
