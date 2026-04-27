from core.api.viewsets.base import BaseViewSet
from core.models import TaskTemplate
from core.serializers import TaskTemplateSyncSerializer


class TaskTemplateViewSet(BaseViewSet):
    queryset = TaskTemplate.objects.all()
    serializer_class = TaskTemplateSyncSerializer
    lookup_field = "uuid"
