from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tasks.models import Task
from tasks.services import is_task_overdue
from users.models import CustomUser


class TasksViewsTestCase(APITestCase):
    """Тестирование бизнес-логики задач"""

    def setUp(self):
        self.moderator = CustomUser.objects.create_user(
            email="mod@test.com", password="Test12345!", full_name="Mod Modov", is_staff=True
        )
        mod_group, _ = Group.objects.get_or_create(name="moderator")
        self.moderator.groups.add(mod_group)

        self.employee = CustomUser.objects.create_user(
            email="emp@test.com", password="Test12345!", full_name="Emp Empov"
        )

        self.client.force_authenticate(user=self.moderator)

    def test_get_important_tasks_endpoint(self):
        """Тест эндпоинта важных задач (покрывает views.py и services.py)"""
        parent = Task.objects.create(
            title="Родительская задача",
            deadline=timezone.now().date() + timedelta(days=5),
            status=Task.TaskStatus.CREATED,
            owner=self.moderator,
        )
        Task.objects.create(
            title="Подзадача",
            deadline=timezone.now().date() + timedelta(days=5),
            status=Task.TaskStatus.PROCESSING,
            employee=self.employee,
            owner=self.moderator,
            parent_task=parent,
        )

        url = reverse("tasks:important-tasks")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["task"], "Родительская задача")

    def test_get_busy_employees_endpoint(self):
        """Тест эндпоинта занятых сотрудников (покрывает views.py и services.py)"""
        Task.objects.create(
            title="Активная задача",
            deadline=timezone.now().date() + timedelta(days=5),
            status=Task.TaskStatus.PROCESSING,
            employee=self.employee,
            owner=self.moderator,
        )

        url = reverse("tasks:busy-employees")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["active_tasks_count"], 1)
        self.assertEqual(response.data[0]["full_name"], "Emp Empov")

    def test_validator_creator_not_employee(self):
        """Тест валидатора: создатель не может быть исполнителем (покрывает validators.py)"""
        task = Task(
            title="Невалидная задача",
            deadline=timezone.now().date() + timedelta(days=5),
            owner=self.moderator,
            employee=self.moderator,
        )
        with self.assertRaises(ValidationError) as context:
            task.full_clean()

        self.assertIn("employee", context.exception.message_dict)

    def test_is_task_overdue_service(self):
        """Тест сервиса проверки просрочки (покрывает services.py)"""
        task = Task(
            title="Просроченная задача",
            deadline=timezone.now().date() - timedelta(days=1),
            status=Task.TaskStatus.PROCESSING,
            employee=self.employee,
            owner=self.moderator,
        )
        self.assertTrue(is_task_overdue(task))

        task.status = Task.TaskStatus.COMPLETED
        self.assertFalse(is_task_overdue(task))
