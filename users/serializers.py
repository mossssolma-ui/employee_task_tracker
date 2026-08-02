from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя"""

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "full_name",
            "date_of_employment",
            "position",
            "status",
            "phone_number",
            "city",
            "avatar",
            "password",
            "is_superuser",
            "is_staff",
            "is_active",
        )
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "is_superuser": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_active": {"read_only": True},
        }

    def create(self, validated_data):
        """Создание пользователя"""
        return CustomUser.objects.create_user(**validated_data)

    def update(self, obj, validated_data):
        """
        Обновление пользователя с хешированием пароля
        """
        password = validated_data.pop("password", None)

        for key, value in validated_data.items():
            setattr(obj, key, value)

        if password:
            obj.set_password(password)

        obj.save()
        return obj
