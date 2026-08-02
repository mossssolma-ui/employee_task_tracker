import random

from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from tasks.models import Task
from users.models import CustomUser


class Command(BaseCommand):
    help = "Создание тестовых пользователей"

    def add_arguments(self, params):
        params.add_argument("--count", type=int, default=10, help="Количество обычных пользователей")
        params.add_argument("--moderators", type=int, default=2, help="Количество модераторов")
        params.add_argument("--clear", action="store_true", help="Очистка таблицы в БД перед заполнением")

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        moderators_count = kwargs["moderators"]
        clear = kwargs["clear"]

        if clear:
            if Task.objects.exists():
                self.stdout.write(self.style.ERROR("Сначала удалите тестовые задачи, а затем пользователей"))
                self.stdout.write(self.style.WARNING("Для этого выполните команду:"))
                self.stdout.write(self.style.WARNING("python manage.py create_test_tasks --clear"))
                return

            deleted_count = CustomUser.objects.filter(is_superuser=False).delete()[0]
            self.stdout.write(self.style.WARNING(f"Удалено {deleted_count} пользователей (кроме суперпользователей)"))

            Group.objects.filter(name="moderator").delete()
            self.stdout.write(self.style.WARNING("Группа 'moderator' удалена"))
            return

        if not clear and CustomUser.objects.filter(is_superuser=False).exists():
            existing_count = CustomUser.objects.filter(is_superuser=False).count()
            self.stdout.write(
                self.style.WARNING(
                    f"Найдено {existing_count} существующих тестовых пользователей. Новые не создаются."
                )
            )
            self.stdout.write(
                self.style.WARNING("Для пересоздания выполните: python manage.py create_test_users --clear")
            )
            return

        moderator_group, created = Group.objects.get_or_create(name="moderator")
        if created:
            self.stdout.write(self.style.SUCCESS('Создана группа "moderator"'))

        users = self.create_test_users(count)
        self.stdout.write(self.style.SUCCESS(f"Создано {len(users)} пользователей"))

        moderators = self.create_test_moderators(moderators_count, moderator_group)
        self.stdout.write(self.style.SUCCESS(f"Создано {len(moderators)} модераторов"))

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 50))
        self.stdout.write(self.style.SUCCESS("Пароль для всех тестовых аккаунтов: test123"))
        self.stdout.write(self.style.SUCCESS("=" * 50))

    def create_test_users(self, count):
        """Создание обычных пользователей"""
        users = []
        first_names = [
            "Ivan",
            "Petr",
            "Sergey",
            "Alexey",
            "Inokentiy",
            "Vyacheslav",
            "Andrei",
            "Anton",
            "Artem",
            "Vladimir",
        ]
        last_names = [
            "Ivanov",
            "Petrov",
            "Sidorov",
            "Smirnov",
            "Kuznetsov",
            "Popov",
            "Vasilev",
            "Lebedev",
            "Kozlov",
            "Novikov",
        ]
        positions = ["Developer", "Tester", "Analyst", "Designer", "DevOps", "Architect"]
        cities = ["Moscow", "St.Peterburg", "Simferopol", "Ekaterinburg", "Kazan", "Tver", "Chelyabinsk", "Sevastopol"]

        password = "test123"

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            full_name = f"{last_name} {first_name}"
            email = f"{last_name.lower()}{first_name.lower()}{random.randint(1, 999)}@example.com"

            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                position=random.choice(positions),
                city=random.choice(cities),
            )

            users.append(user)
            self.stdout.write(f"Создан: {user.full_name} ({user.email})")

        return users

    def create_test_moderators(self, count, moderator_group):
        """Создание модераторов"""
        moderators = []
        first_names = [
            "Svetlana",
            "Vasilisa",
            "Ekaterina",
            "Alexa",
            "Anya",
            "Ludmila",
            "Vika",
            "Kristina",
            "Olya",
            "Alexandra",
        ]
        last_names = [
            "Ivanova",
            "Petrova",
            "Sidorova",
            "Smirnova",
            "Kuznetsova",
            "Popova",
            "Vasileva",
            "Lebedeva",
            "Kozlova",
            "Novikova",
        ]
        cities = ["Moscow", "St.Peterburg", "Simferopol", "Ekaterinburg", "Kazan", "Tver", "Chelyabinsk", "Sevastopol"]

        password = "test123"

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            full_name = f"{last_name} {first_name}"
            email = f"moderator.{last_name.lower()}{first_name.lower()}{random.randint(1, 999)}@example.com"

            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                position="Moderator",
                city=random.choice(cities),
                is_staff=True,
            )

            user.groups.add(moderator_group)
            user.save()

            moderators.append(user)
            self.stdout.write(f"Создан модератор: {user.full_name} ({user.email})")

        return moderators
