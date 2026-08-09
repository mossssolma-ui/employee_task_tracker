from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


def health_check(request):
    """Эндроинт для healthcheck"""
    return JsonResponse({"status": "ok"})


schema_view = get_schema_view(
    openapi.Info(
        title="Трекер задач сотрудников API",
        default_version="v1",
        description="API для трекера задач сотрудников",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mossssolma@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("health/", health_check),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("", include("tasks.urls", namespace="tasks")),
]
