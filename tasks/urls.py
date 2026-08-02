from django.urls import include, path
from rest_framework import routers

from tasks.apps import TasksConfig
from tasks.views import BusyEmployeesAPIView, ImportantTasksAPIView, OverdueTasksAPIView, TaskViewSet

app_name = TasksConfig.name

router = routers.DefaultRouter()
router.register(r"", TaskViewSet, basename="tasks")

urlpatterns = [
    path("overdue/", OverdueTasksAPIView.as_view(), name="overdue-tasks"),
    path("busy_employees/", BusyEmployeesAPIView.as_view(), name="busy-employees"),
    path("important/", ImportantTasksAPIView.as_view(), name="important-tasks"),
    path("", include(router.urls)),
]
