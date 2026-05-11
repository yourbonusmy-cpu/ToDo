from uuid import UUID

from core.models import TaskTemplate
from core.services.sync.common.conflict import resolve_update
from core.services.sync.common.time import safe_parse_dt
from core.services.sync.common.uuid import as_uuid_map


def sync_templates(request, user, items, files):

    existing = as_uuid_map(TaskTemplate.objects.filter(owner=user))

    uploaded_icons = []

    for data in items:

        uuid = UUID(data["uuid"])

        client_created_at = safe_parse_dt(data.get("created_at"))

        client_updated_at = safe_parse_dt(data.get("updated_at"))

        obj = existing.get(uuid)

        icon = files.get(f"icon_{uuid}")

        # =====================================================
        # UPDATE
        # =====================================================

        if obj:

            if not resolve_update(
                obj,
                data,
                client_updated_at,
                obj.updated_at,
            ):
                continue

            obj.title = data.get("title", obj.title)

            obj.description = data.get("description", obj.description)

            obj.priority = data.get("priority", obj.priority)

            obj.is_hidden = data.get("is_hidden", obj.is_hidden)

            obj.amount = data.get("amount", obj.amount)

            obj.time = data.get("time", obj.time)

            obj.period_type = data.get("period_type", obj.period_type)

            obj.schedule_type = data.get("schedule_type", obj.schedule_type)

            obj.fixed_weekday = data.get("fixed_weekday", obj.fixed_weekday)

            obj.fixed_day_of_month = data.get(
                "fixed_day_of_month", obj.fixed_day_of_month
            )

            obj.fixed_month_of_year = data.get(
                "fixed_month_of_year", obj.fixed_month_of_year
            )

            obj.selected_count = data.get("selected_count", obj.selected_count)

            # ---------------- ICON ----------------

            if icon:

                # удалить старую
                if obj.icon:
                    obj.icon.delete(save=False)

                obj.icon = icon

            # ---------------- UPDATED_AT ----------------

            if client_updated_at:
                obj.updated_at = client_updated_at

            obj.save()

        # =====================================================
        # CREATE
        # =====================================================

        else:

            obj = TaskTemplate.objects.create(
                owner=user,
                uuid=uuid,
                title=data.get("title", ""),
                description=data.get("description", ""),
                priority=data.get("priority", 0),
                is_hidden=data.get("is_hidden", False),
                amount=data.get("amount", 1),
                time=data.get("time", 0),
                period_type=data.get("period_type"),
                schedule_type=data.get("schedule_type"),
                fixed_weekday=data.get("fixed_weekday"),
                fixed_day_of_month=data.get("fixed_day_of_month"),
                fixed_month_of_year=data.get("fixed_month_of_year"),
                selected_count=data.get("selected_count", 0),
                icon=icon,
                created_at=client_created_at,
                updated_at=client_updated_at,
            )

        # =====================================================
        # RESPONSE ICONS
        # =====================================================

        if obj.icon:
            uploaded_icons.append(
                {
                    "template_uuid": str(obj.uuid),
                    # FULL URL
                    "icon": request.build_absolute_uri(obj.icon.url),
                }
            )

    return uploaded_icons
