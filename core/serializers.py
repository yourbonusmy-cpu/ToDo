from rest_framework import serializers
from core.models import Device
from core.models import (
    Block,
    BlockTask,
    TaskTemplate,
    GroupTemplate,
    DeletedObject,
    SystemTaskTemplate,
)


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = [
            "uuid",
            "title",
            "priority",
            "is_hidden",
            "created_at",
            "updated_at",
            "target_date",
        ]


class BlockTaskSerializer(serializers.ModelSerializer):
    block_uuid = serializers.UUIDField(source="block.uuid")
    template_uuid = serializers.UUIDField(source="template.uuid", allow_null=True)

    class Meta:
        model = BlockTask
        fields = [
            "uuid",
            "block_uuid",
            "template_uuid",
            "title",
            "description",
            "icon",
            "position",
            "amount",
            "time",
            "is_hidden",
            "is_encrypted",
            "created_at",
            "updated_at",
        ]


class SystemTaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemTaskTemplate
        exclude = ["id"]


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        exclude = ["id", "owner"]


class GroupTemplateSerializer(serializers.ModelSerializer):
    task_uuids = serializers.PrimaryKeyRelatedField(
        many=True, source="tasks", read_only=True
    )

    class Meta:
        model = GroupTemplate
        exclude = ["id", "owner"]


class DeletedObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeletedObject
        fields = ["obj_uuid", "object_type", "deleted_at"]


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "device_id",
            "platform",
            "name",
            "last_sync_at",
            "last_seen_at",
            "created_at",
            "is_active",
        ]
        read_only_fields = [
            "last_seen_at",
            "created_at",
            "last_sync_at",
        ]


class TaskTemplateSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = [
            "uuid",
            "title",
            "description",
            "icon",
            "amount",
            "time",
            "period_type",
            "schedule_type",
            "fixed_weekday",
            "fixed_day_of_month",
            "fixed_month_of_year",
            "priority",
            "updated_at",
        ]
