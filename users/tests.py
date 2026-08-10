from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import CustomUser


class UserViewsTestCase(APITestCase):
    """Тестирование пользователей"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@test.com", password="Test12345!", full_name="Test Testovich"
        )

        self.moderator = CustomUser.objects.create_user(
            email="mod@test.com", password="Test12345!", full_name="Mod Moderator", is_staff=True
        )
        moderator_group, _ = Group.objects.get_or_create(name="moderator")
        self.moderator.groups.add(moderator_group)

        self.admin = CustomUser.objects.create_superuser(
            email="admin@test.com", password="Admin123!", full_name="Admin Adminovich"
        )

    def test_user_create(self):
        """Тест регистрации нового пользователя"""
        url = reverse("users:register")
        data = {"email": "newuser@test.com", "password": "StrongPass123!", "full_name": "New User"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email="newuser@test.com").exists())

    def test_user_create_duplicate_email(self):
        """Тест регистрации с существующим email"""
        url = reverse("users:register")
        data = {"email": "test@test.com", "password": "Test12345!"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()["message"], "Пользователь с таким email уже существует")

    def test_user_list_forbidden_for_regular_user(self):
        """Тест, обычный пользователь НЕ может получить список всех пользователей"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_for_moderator(self):
        """Тест, модератор МОЖЕТ получить список всех пользователей"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("users:user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_retrieve_own_profile(self):
        """Тест, пользователь может получить свой профиль"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-retrieve", args=[self.user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], self.user.email)

    def test_user_retrieve_other_profile_forbidden(self):
        """Тест, пользователь НЕ может получить чужой профиль"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-retrieve", args=[self.moderator.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_update_own_profile(self):
        """Тест, пользователь может обновить свой профиль"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-update", args=[self.user.pk])
        data = {"full_name": "Updated Name"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Updated Name")

    def test_user_update_other_profile_forbidden(self):
        """Тест, пользователь НЕ может обновить чужой профиль"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-update", args=[self.moderator.pk])
        data = {"full_name": "Hacked!"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_delete_own_profile(self):
        """Тест, пользователь НЕ может удалить свой профиль (только админ)"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-delete", args=[self.user.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CustomUser.objects.filter(pk=self.user.pk).exists())

    def test_user_delete_other_profile_forbidden(self):
        """Тест, пользователь НЕ может удалить чужой профиль"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-delete", args=[self.moderator.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_user(self):
        """Тест, администратор может удалить любого пользователя"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("users:user-delete", args=[self.user.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())

    def test_moderator_can_update_any_profile(self):
        """Тест, модератор может обновить профиль любого пользователя"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("users:user-update", args=[self.user.pk])
        data = {"full_name": "Updated moderator"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_any_profile(self):
        """Тест, администратор может обновить профиль любого пользователя"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("users:user-update", args=[self.user.pk])
        data = {"full_name": "Updated admin"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
