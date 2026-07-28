from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.models import CustomUser
from users.serializers import CustomUserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация пользователя"""

    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            return Response({"message": "Пользователь существует"}, status=status.HTTP_409_CONFLICT)
        return super().create(request, *args, **kwargs)


class UserListAPIView(generics.ListAPIView):
    """Просмотр всех пользователей (для суперюзера)"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр/Обновление/Удаление пользователя"""

    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
