from core.api.viewsets.base import BaseViewSet
from core.models import BlockTask
from core.serializers import BlockTaskSerializer


class BlockTaskViewSet(BaseViewSet):
    queryset = BlockTask.objects.all()
    serializer_class = BlockTaskSerializer
    lookup_field = "uuid"
