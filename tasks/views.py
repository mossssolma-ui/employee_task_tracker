from django.db.models import Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Task
from tasks.paginators import CustomPaginator
from tasks.permissions import IsOwner
from tasks.serializers import TaskSerializer
from tasks.services import (
    get_busy_employees,
    get_important_tasks,
    get_overdue_tasks,
    get_potential_employees_for_important_task,
)
from users.permissions import IsModerator


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD для задач"""

    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    pagination_class = CustomPaginator

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("status", "priority", "employee", "owner", "deadline")
    ordering_fields = ("created_at", "deadline", "priority", "status", "title")
    ordering = ("-priority", "deadline")

    def get_queryset(self):
        """Возвращает задачи доступные пользователю"""
        user = self.request.user

        if user.is_anonymous:
            return Task.objects.none()

        if user.groups.filter(name="moderator").exists():
            return Task.objects.all()
        return Task.objects.filter(employee=user)

    def perform_create(self, serializer):
        """Задача при создании привязывается к текущему пользователю (владельцу)"""
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        """Передача request в контекст сериализатора"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_permissions(self):
        """Назначение прав доступа при различных действиях"""
        if self.action == "create":
            self.permission_classes = [IsModerator]
        elif self.action == "destroy":
            self.permission_classes = [IsOwner]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_description="Получить список задач с пагинацией и общей статистикой по ним",
        responses={
            200: openapi.Response(
                description="Список задач и статистика",
                examples={
                    "application/json": {
                        "count": 10,
                        "next": "http://localhost:8000/tasks/?page=2",
                        "previous": None,
                        "statistics": {
                            "total": 10,
                            "created_count": 2,
                            "processing_count": 5,
                            "completed": 2,
                            "cancelled": 1,
                            "overdue": 1,
                            "very_high_count": 4,
                            "high_count": 3,
                            "medium_count": 1,
                            "low_count": 1,
                            "important_count": 2,
                        },
                        "results": [
                            {
                                "id": 1,
                                "title": "Разработать API",
                                "status": "processing",
                                "priority": "high",
                                "deadline": "2024-12-31",
                            }
                        ],
                    }
                },
            )
        },
    )
    def list(self, request, *args, **kwargs):
        """Переопределение list для возврата статистики"""
        queryset = self.filter_queryset(self.get_queryset().select_related("employee", "owner"))

        stats = queryset.aggregate(
            total=Count("id"),
            created=Count("id", filter=Q(status=Task.TaskStatus.CREATED)),
            processing=Count("id", filter=Q(status=Task.TaskStatus.PROCESSING)),
            completed=Count("id", filter=Q(status=Task.TaskStatus.COMPLETED)),
            cancelled=Count("id", filter=Q(status=Task.TaskStatus.CANCELLED)),
            overdue=Count(
                "id",
                filter=Q(
                    deadline__lt=timezone.now().date(),
                    status__in=[Task.TaskStatus.CREATED, Task.TaskStatus.PROCESSING],
                ),
            ),
            very_high=Count("id", filter=Q(priority=Task.TaskPriority.VERY_HIGH)),
            high=Count("id", filter=Q(priority=Task.TaskPriority.HIGH)),
            medium=Count("id", filter=Q(priority=Task.TaskPriority.MEDIUM)),
            low=Count("id", filter=Q(priority=Task.TaskPriority.LOW)),
        )

        important_count = (
            Task.objects.filter(status=Task.TaskStatus.CREATED, subtasks__status=Task.TaskStatus.PROCESSING)
            .distinct()
            .count()
        )

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "count": self.paginator.page.paginator.count,
                    "next": self.paginator.get_next_link(),
                    "previous": self.paginator.get_previous_link(),
                    "statistics": {
                        "total": stats["total"],
                        "created_count": stats["created"],
                        "processing_count": stats["processing"],
                        "completed": stats["completed"],
                        "cancelled": stats["cancelled"],
                        "overdue": stats["overdue"],
                        "very_high_count": stats["very_high"],
                        "high_count": stats["high"],
                        "medium_count": stats["medium"],
                        "low_count": stats["low"],
                        "important_count": important_count,
                    },
                    "results": serializer.data,
                }
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "statistics": {
                    "total": stats["total"],
                    "created_count": stats["created"],
                    "processing_count": stats["processing"],
                    "completed": stats["completed"],
                    "cancelled": stats["cancelled"],
                    "overdue": stats["overdue"],
                    "very_high_count": stats["very_high"],
                    "high_count": stats["high"],
                    "medium_count": stats["medium"],
                    "low_count": stats["low"],
                    "important_count": important_count,
                },
                "results": serializer.data,
            }
        )


class OverdueTasksAPIView(APIView):
    """
    Просроченные задачи.
    """

    @swagger_auto_schema(
        operation_description="Получить список всех просроченных задач",
        responses={
            200: TaskSerializer(many=True),
            401: "Необходима авторизация",
        },
    )
    def get(self, request):
        tasks = get_overdue_tasks()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class BusyEmployeesAPIView(APIView):
    """
    Занятые сотрудники. Запрашивает из БД список сотрудников и их задачи,
    отсортированный по количеству активных задач.
    """

    permission_classes = [IsModerator]

    @swagger_auto_schema(
        operation_description="Получить список занятых сотрудников и их активных задач (доступно модераторам)",
        responses={
            200: openapi.Response(
                description="Список сотрудников с задачами",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "full_name": "Ivanov Ivan",
                            "position": "Developer",
                            "active_tasks_count": 3,
                            "tasks": [{"id": 5, "title": "Разработать API", "status": "processing"}],
                        }
                    ]
                },
            ),
            403: "Доступ запрещен (требуются права модератора)",
        },
    )
    def get(self, request):
        busy_employees = get_busy_employees()
        response_data = []

        for employee in busy_employees:
            tasks = employee.employee_tasks.filter(status=Task.TaskStatus.PROCESSING)
            tasks_data = TaskSerializer(tasks, many=True, context={"request": request})
            response_data.append(
                {
                    "id": employee.id,
                    "full_name": employee.full_name,
                    "position": employee.position,
                    "active_tasks_count": employee.active_tasks_count,
                    "tasks": tasks_data.data,
                }
            )

        return Response(response_data)


class ImportantTasksAPIView(APIView):
    """
    Важные задачи - задачи, не взятые в работу,
    но от которых зависят другие задачи, взятые в работу.
    Также возвращает список кандидатов для каждой задачи.
    """

    permission_classes = [IsModerator]

    @swagger_auto_schema(
        operation_description="Получить список важных задач и рекомендованных исполнителей "
        "для них (доступно модераторам)",
        responses={
            200: openapi.Response(
                description="Список важных задач с кандидатами",
                examples={
                    "application/json": [
                        {
                            "task": "Спроектировать архитектуру",
                            "deadline": "2024-12-31",
                            "candidates": ["Petrov Petr", "Sidorov Ivan"],
                        }
                    ]
                },
            ),
            403: "Доступ запрещен (требуются права модератора)",
        },
    )
    def get(self, request):
        important_tasks = get_important_tasks()
        result = get_potential_employees_for_important_task(important_tasks)
        return Response(result)
