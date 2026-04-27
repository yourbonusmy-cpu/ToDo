from core.api.viewsets.base import BaseViewSet
from core.models import Device
from core.serializers import DeviceSerializer


class DeviceViewSet(BaseViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
