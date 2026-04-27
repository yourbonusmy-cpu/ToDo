from rest_framework.viewsets import ModelViewSet

from core.api.viewsets.base import BaseViewSet
from core.models import Block
from core.serializers import BlockSerializer


class BlockViewSet(BaseViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    lookup_field = "uuid"
