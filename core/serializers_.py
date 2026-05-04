# serializers_.py

from rest_framework import serializers

from config import settings
from core.models import Block, BlockTask, TaskTemplate, GroupTemplate


class BlockTaskSerializer(serializers.ModelSerializer):
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
            "created_at",
            "updated_at",
        ]

    def get_icon(self, obj):
        request = self.context.get("request")

        if not obj.icon:
            return None

        if isinstance(obj.icon, str):
            return request.build_absolute_uri(settings.MEDIA_URL + obj.icon)


class BlockSerializer(serializers.ModelSerializer):
    block_tasks = BlockTaskSerializer(many=True)

    class Meta:
        model = Block
        read_only_fields = ["id", "created_at", "updated_at"]
        exclude = ["owner"]

    def update(self, instance, validated_data):
        block_tasks_data = validated_data.pop("block_tasks", [])

        # --- обновление блока ---
        instance.title = validated_data.get("title", instance.title)
        instance.target_date = validated_data.get("target_date", instance.target_date)
        instance.priority = validated_data.get("priority", instance.priority)
        instance.save()

        # --- текущие задачи ---
        existing_block_tasks = {str(t.id): t for t in instance.block_tasks.all()}
        used_ids = set()
        new_block_tasks = []

        for position, block_task_data in enumerate(block_tasks_data):
            task_id = str(block_task_data.get("id"))

            if task_id in existing_block_tasks:
                task = existing_block_tasks[task_id]

                for attr, value in block_task_data.items():
                    setattr(task, attr, value)

                task.position = position
                task.save()

                used_ids.add(task_id)

            else:
                new_block_tasks.append(
                    BlockTask(block=instance, position=position, **block_task_data)
                )

        for task_id, task in existing_block_tasks.items():
            if task_id not in used_ids:
                task.delete()

        if new_block_tasks:
            BlockTask.objects.bulk_create(new_block_tasks)

        return instance


class GroupTaskSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = TaskTemplate
        fields = [  # лучше явно указывать, чем exclude
            "id",
            "title",
            "description",
            "icon",
            "default_amount",
            "period_type",
            "schedule_type",
            "fixed_weekday",
            "fixed_day_of_month",
            "fixed_month_of_year",
            "priority",
            "created_at",
            "updated_at",
        ]

    def get_icon(self, obj):
        request = self.context.get("request")
        if request and obj.icon and getattr(obj.icon, "name", None):
            return request.build_absolute_uri(obj.icon.url)
        return None


class GroupTemplateSerializer(serializers.ModelSerializer):
    tasks = GroupTaskSerializer(many=True, read_only=True)

    class Meta:
        model = GroupTemplate
        fields = [
            "id",
            "title",
            "description",
            "selected_count",
            "tasks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaskTemplateSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = TaskTemplate
        fields = [
            "id",
            "title",
            "description",
            "icon",
            "default_amount",
            "period_type",
            "schedule_type",
            "fixed_weekday",
            "fixed_day_of_month",
            "fixed_month_of_year",
            "created_at",
            "updated_at",
        ]

    def get_icon(self, obj):
        request = self.context.get("request")

        if obj.icon and obj.icon.name:
            return request.build_absolute_uri(obj.icon.url)

        return None
