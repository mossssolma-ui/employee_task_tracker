from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from users.models import CustomUser
from users.permissions import IsModerator
from users.serializers import CustomUserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация пользователя"""

    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        request_body=CustomUserSerializer,
        responses={
            201: CustomUserSerializer,
            409: "Пользователь с таким email уже существует",
        },
    )
    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            return Response({"message": "Пользователь с таким email уже существует"}, status=status.HTTP_409_CONFLICT)
        return super().create(request, *args, **kwargs)


class UserListAPIView(generics.ListAPIView):
    """Просмотр списка всех пользователей"""

    permission_classes = [IsModerator | IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Просмотр всех пользователей (доступно модераторам и админам)",
        responses={
            200: CustomUserSerializer(many=True),
            403: "Доступ запрещен (требуются права модератора или админа)",
        },
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Детальная информация о пользователе"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Получить информацию о пользователе по ID. Обычный пользователь видит только себя.",
        responses={200: CustomUserSerializer, 404: "Пользователь не найден или нет прав доступа"},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderator").exists():
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)


class UserUpdateAPIView(generics.UpdateAPIView):
    """Обновление данных пользователя"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Полное обновление данных пользователя (PUT)",
        request_body=CustomUserSerializer,
        responses={
            200: CustomUserSerializer,
            400: "Ошибка валидации данных",
            403: "Доступ запрещен",
            404: "Пользователь не найден",
        },
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частичное обновление данных пользователя (PATCH)",
        request_body=CustomUserSerializer,
        responses={
            200: CustomUserSerializer,
            400: "Ошибка валидации данных",
            403: "Доступ запрещен",
            404: "Пользователь не найден",
        },
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderator").exists():
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)


class UserDestroyAPIView(generics.DestroyAPIView):
    """Удаление пользователя"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Удалить пользователя (доступно админам и модераторам, либо пользователю самому себе)",
        responses={204: "Пользователь успешно удален", 403: "Доступ запрещен", 404: "Пользователь не найден"},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderator").exists():
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)
