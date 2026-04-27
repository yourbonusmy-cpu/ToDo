from rest_framework.routers import DefaultRouter

from core.api.viewsets.sync import SyncViewSet
from core.api.viewsets.blocks import BlockViewSet
from core.api.viewsets.block_task import BlockTaskViewSet
from core.api.viewsets.task_templates import TaskTemplateViewSet
from core.api.viewsets.system_templates import SystemTaskTemplateViewSet
from core.api.viewsets.group_templates import GroupTemplateViewSet
from core.api.viewsets.devices import DeviceViewSet

router = DefaultRouter()

router.register("sync", SyncViewSet, basename="sync")
router.register("blocks", BlockViewSet, basename="blocks")
router.register("block-tasks", BlockTaskViewSet, basename="block-tasks")
router.register("task-templates", TaskTemplateViewSet, basename="task-templates")
router.register(
    "system-templates", SystemTaskTemplateViewSet, basename="system-templates"
)
router.register("group-templates", GroupTemplateViewSet, basename="group-templates")
router.register("devices", DeviceViewSet, basename="devices")

urlpatterns = router.urls
