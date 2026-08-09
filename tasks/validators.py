from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_deadline(task):
    """
    Проверяет дату дедлайна, должна быть не в прошлом
    """
    if task.deadline and task.deadline < timezone.now().date():
        raise ValidationError({"deadline": "Срок выполнения не может быть в прошлом"})


def validate_title_length(task):
    """
    Проверка, что поле не пустое
    """
    if len(task.title) < 1:
        raise ValidationError({"title": "Название задачи не может быть пустое"})
    if len(task.title) > 300:
        raise ValidationError({"title": "Название задачи не может превышать 300 символов"})


def validate_owner_not_employee(task):
    """
    Проверяет, что владелец задачи не является ее исполнителем
    """
    if task.owner_id and task.employee_id and task.owner_id == task.employee_id:
        raise ValidationError({"employee": "Создатель задачи не может быть ее исполнителем"})


def validate_no_self_parent(task):
    """
    Проверка, что задача не является родительской для самой себя
    """
    if task.parent_task_id and task.parent_task_id == task.pk:
        raise ValidationError({"parent_task": "Задача не может быть родительской для самой себя"})


def validate_status(task):
    """Проверяет, что статус присвоился при создании задачи"""
    if task.status in ("processing", "completed") and not task.employee:
        raise ValidationError({"status": "Задача не может выполняться (или быть выполненной) без исполнителя"})


def validate_employee_is_active(task):
    """
    Проверяет, что исполнитель активен и не уволен
    """
    if task.employee:
        if not task.employee.is_active:
            raise ValidationError({"employee": "Исполнитель не активен в системе"})

        if task.employee.status == task.employee.EmployeeStatus.DISMISSED:
            raise ValidationError({"employee": "Исполнитель уволен"})


def validate_no_task_repeat(task):
    """
    Проверяет отсутствие циклической зависимости задач
    """
    if task.parent_task:
        cur = task.parent_task
        visit = set()

        while cur:
            if cur.id == task.id:
                raise ValidationError({"parent_task": "Обнаружена циклическая зависимость задач"})

            if cur.id in visit:
                break

            visit.add(cur.id)
            cur = cur.parent_task
