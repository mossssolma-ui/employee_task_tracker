from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


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
        ACTIVE = "active", "Работает"
        VACATION = "vacation", "В отпуске"
        MISSION = "mission", "В командировке"
        SICK_LEAVE = "sick_leave", "На больничном"
        DISMISSED = "dismissed", "Уволен"

    username = None
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Укажите почту")
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Имя", help_text="Укажите имя")
    last_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Фамилия", help_text="Укажите фамилию"
    )
    position = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Должность", help_text="Укажите должность сотрудника"
    )
    phone_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Телефон", help_text="Укажите телефон"
    )
    date_of_employment = models.DateField(
        default=timezone.now, verbose_name="Дата приема на работу", help_text="Укажите дату приема на работу"
    )
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.ACTIVE,
        verbose_name="Статус сотрудника",
        help_text="Укажите текущий статус сотрудника",
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город", help_text="Укажите город")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите аватар"
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
        if self.last_name and self.first_name:
            return f"{self.last_name} {self.first_name} ({self.get_status_display()})"
        return f"{self.email} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-email"]
