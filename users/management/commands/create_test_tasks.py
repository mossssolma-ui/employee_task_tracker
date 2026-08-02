import random
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.utils import timezone

from tasks.models import Task
from users.models import CustomUser


class Command(BaseCommand):
    help = "Создание тестовых задач"

    def add_arguments(self, params):
        params.add_argument("--count", type=int, default=20, help="Количество задач")
        params.add_argument("--clear", action="store_true", help="Очистка таблицы перед заполнением")

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        clear = kwargs["clear"]

        if clear:
            Task.objects.all().delete()
            self.stdout.write(self.style.WARNING("Все задачи удалены"))
            return

        moderator_group = Group.objects.filter(name="moderator").first()
        if not moderator_group:
            self.stdout.write(self.style.ERROR('Группа "moderator" не найдена. Сначала запустите create_test_users'))
            return

        moderators = CustomUser.objects.filter(
            groups=moderator_group, is_active=True, is_staff=True, is_superuser=False
        )
        if not moderators.exists():
            self.stdout.write(self.style.ERROR("Нет активных модераторов."))
            return

        employees = CustomUser.objects.filter(is_active=True, status=CustomUser.EmployeeStatus.ACTIVE).exclude(
            groups=moderator_group
        )

        if Task.objects.exists():
            self.stdout.write(
                self.style.WARNING(f"Найдено {Task.objects.count()} существующих задач. Новые не создаются.")
            )
            self.stdout.write(
                self.style.WARNING("Для пересоздания выполните: python manage.py create_test_tasks --clear")
            )
            return

        created_tasks = 0
        created_overdue = 0
        created_important = 0

        for i in range(count):
            owner = random.choice(moderators)
            has_employee = random.random() > 0.3
            employee = random.choice(employees) if (has_employee and employees.exists()) else None

            deadline = timezone.now().date() + timedelta(days=random.randint(1, 60))

            if employee:
                status = random.choice(
                    [
                        Task.TaskStatus.CREATED,
                        Task.TaskStatus.PROCESSING,
                        Task.TaskStatus.COMPLETED,
                        Task.TaskStatus.CANCELLED,
                    ]
                )
                if status == Task.TaskStatus.CREATED:
                    status = Task.TaskStatus.PROCESSING
            else:
                status = Task.TaskStatus.CREATED

            priority = random.choice(
                [Task.TaskPriority.LOW, Task.TaskPriority.MEDIUM, Task.TaskPriority.HIGH, Task.TaskPriority.VERY_HIGH]
            )

            task = Task.objects.create(
                owner=owner,
                employee=employee,
                title=random.choice(self.get_task_titles()),
                description=random.choice(self.get_descriptions()),
                deadline=deadline,
                status=status,
                priority=priority,
            )

            created_tasks += 1
            is_overdue = False
            if random.random() < 0.30 and status not in [Task.TaskStatus.COMPLETED, Task.TaskStatus.CANCELLED]:
                past_deadline = timezone.now().date() - timedelta(days=random.randint(1, 30))
                Task.objects.filter(id=task.id).update(deadline=past_deadline)
                task.deadline = past_deadline
                is_overdue = True
                created_overdue += 1

            if random.random() < 0.15 and employees.exists():
                task.deadline = timezone.now().date() + timedelta(days=random.randint(10, 30))
                task.employee = None
                task.status = Task.TaskStatus.CREATED
                task.save()

                subtask = Task.objects.create(
                    owner=owner,
                    employee=random.choice(employees),
                    title=f"Подзадача: {task.title}",
                    description=f"Часть задачи '{task.title}'",
                    parent_task=task,
                    deadline=task.deadline + timedelta(days=random.randint(1, 10)),
                    status=Task.TaskStatus.PROCESSING,
                    priority=Task.TaskPriority.MEDIUM,
                )
                created_important += 1
                self.stdout.write(self.style.SUCCESS(f"Создана важная зависимость: {subtask.title}"))

            emp_name = getattr(employee, "full_name", "Нет") or "Нет"
            self.stdout.write(
                f"Создана задача: {task.title} (статус: {task.get_status_display()}, "
                f"исп: {emp_name}, просрочена: {is_overdue})"
            )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 50))
        self.stdout.write(self.style.SUCCESS(f"Всего создано задач: {created_tasks}"))
        self.stdout.write(self.style.SUCCESS(f"Просроченных: {created_overdue}"))
        self.stdout.write(self.style.SUCCESS(f"Важных (с зависимыми подзадачами): {created_important}"))
        self.stdout.write(self.style.SUCCESS("=" * 50))

    def get_task_titles(self):
        return [
            "Спроектировать архитектуру",
            "Разработать API",
            "Написать документацию",
            "Провести тестирование",
            "Оптимизировать запросы",
            "Настроить CI/CD",
            "Разработать интерфейс",
            "Создать миграции",
            "Написать юнит-тесты",
            "Настроить мониторинг",
            "Провести code review",
            "Обновить зависимости",
        ]

    def get_descriptions(self):
        return [
            "Необходимо спроектировать систему с нуля",
            "Разработать REST API с документацией",
            "Подготовить документацию для пользователей",
            "Провести полное тестирование функционала",
            "Оптимизировать SQL запросы для улучшения производительности",
            "Настроить автоматическую сборку и деплой",
        ]
