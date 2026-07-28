import os

from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = "add create superuser"

    def handle(self, *args, **options):
        email = os.getenv("CSU_EMAIL")
        password = os.getenv("CSU_PASSWORD")

        if not email or not password:
            self.stdout.write(self.style.ERROR("Не указаны email и password в .env файле"))
            return

        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Пользователь с email: {email} уже существует"))
            return

        user = CustomUser.objects.create(email=email)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Администратор с email: {email} успешно создан"))
