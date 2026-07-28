from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя"""

    full_name = serializers.SerializerMethodField()

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
            "password": {"write_only": True},
            "is_superuser": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_active": {"read_only": True},
        }

    def create(self, validated_data):
        """Создание пользователя"""
        return CustomUser.objects.create_user(**validated_data)

    def get_full_name(self, obj):
        """Возврат полного имени и фамилии пользователя"""
        if obj.last_name and obj.first_name:
            return f"{obj.last_name} {obj.first_name[0]}"
        return obj.last_name
