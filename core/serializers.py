# serializers.py

from rest_framework import serializers

from config import settings
from core.models import Block, BlockTask


class TaskSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = BlockTask
        fields = [
            "id",
            "title",
            "description",
            "icon",
            "amount",
            "time",
            "is_hidden",
            "is_encrypted",
        ]

    def get_icon(self, obj):
        request = self.context.get("request")

        if not obj.icon:
            return None

        # если уже строка (старые данные)
        if isinstance(obj.icon, str):
            return request.build_absolute_uri(settings.MEDIA_URL + obj.icon)

        # если FileField
        try:
            return request.build_absolute_uri(obj.icon.url)
        except Exception:
            return None


class BlockSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Block
        fields = ["id", "title", "target_date", "tasks"]
