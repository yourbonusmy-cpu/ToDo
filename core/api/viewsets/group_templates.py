from core.api.viewsets.base import BaseViewSet
from core.models import GroupTemplate
from core.serializers import GroupTemplateSerializer


class GroupTemplateViewSet(BaseViewSet):
    queryset = GroupTemplate.objects.all()
    serializer_class = GroupTemplateSerializer
    lookup_field = "uuid"
