from rest_framework import viewsets

from core.models import SystemTaskTemplate
from core.serializers import SystemTaskTemplateSerializer


class SystemTaskTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemTaskTemplate.objects.filter(is_hidden=False)
    serializer_class = SystemTaskTemplateSerializer
    lookup_field = "uuid"
