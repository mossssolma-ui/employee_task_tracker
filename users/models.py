import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("status", CustomUser.EmployeeStatus.ACTIVE)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", CustomUser.EmployeeStatus.ACTIVE)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя для трекера задач сотрудников"""

    class EmployeeStatus(models.TextChoices):
        """Статус сотрудника"""

        ACTIVE = "active", "Работает"
        VACATION = "vacation", "В отпуске"
        MISSION = "mission", "В командировке"
        SICK_LEAVE = "sick_leave", "На больничном"
        DISMISSED = "dismissed", "Уволен"

    username = None
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Укажите почту")
    phone_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Телефон", help_text="Укажите телефон"
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город", help_text="Укажите город")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите аватар"
    )
    full_name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="ФИО", help_text="Укажите ФИО сотрудника"
    )
    position = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Должность", help_text="Укажите должность сотрудника"
    )
    date_of_employment = models.DateField(
        default=datetime.date.today, verbose_name="Дата приема на работу", help_text="Укажите дату приема на работу"
    )
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.ACTIVE,
        verbose_name="Статус сотрудника",
        help_text="Укажите текущий статус сотрудника",
    )

    is_active = models.BooleanField(
        default=True, verbose_name="Активен в системе", help_text="Может ли пользователь входить в систему"
    )
    is_staff = models.BooleanField(default=False, verbose_name="Доступ к админке")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.full_name} {self.position} {self.status} {self.date_of_employment}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-email"]
