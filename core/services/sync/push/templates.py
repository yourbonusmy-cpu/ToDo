from uuid import UUID
import json

from core.models import TaskTemplate
from core.services.sync.common.conflict import resolve_update
from core.services.sync.common.time import safe_parse_dt
from core.services.sync.common.uuid import as_uuid_map


def sync_templates(user, items, files):

    print("\n========== SYNC TEMPLATES START ==========")

    print("USER:", user)

    print("\nFILES:")
    print(files)

    for key, file in files.items():
        print(
            "FILE:",
            key,
            "| NAME:",
            file.name,
            "| SIZE:",
            file.size,
            "| CONTENT_TYPE:",
            file.content_type,
        )

    print("\nITEMS:")
    print(json.dumps(items, indent=4, ensure_ascii=False))

    existing = as_uuid_map(TaskTemplate.objects.filter(owner=user))

    for data in items:

        print("\n----------------------------------")
        print("PROCESS TEMPLATE:")
        print(json.dumps(data, indent=4, ensure_ascii=False))

        try:

            uuid = UUID(data["uuid"])

            print("UUID:", uuid)

            client_created_at = safe_parse_dt(data.get("created_at"))

            client_updated_at = safe_parse_dt(data.get("updated_at"))

            print("CLIENT CREATED:", client_created_at)
            print("CLIENT UPDATED:", client_updated_at)

            obj = existing.get(uuid)

            icon = files.get(f"icon_{uuid}")

            print("ICON FOUND:", icon is not None)

            if icon:
                print("ICON NAME:", icon.name)
                print("ICON SIZE:", icon.size)

            # =====================================================
            # UPDATE
            # =====================================================

            if obj:

                print("MODE: UPDATE")

                allow_update = resolve_update(
                    obj,
                    data,
                    client_updated_at,
                    obj.updated_at,
                )

                print("RESOLVE UPDATE:", allow_update)

                if not allow_update:
                    print("SKIP UPDATE")
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

                    print("UPDATE ICON")

                    if obj.icon:
                        print("DELETE OLD ICON:", obj.icon.name)
                        obj.icon.delete(save=False)

                    obj.icon = icon

                # ---------------- UPDATED_AT ----------------

                if client_updated_at:
                    obj.updated_at = client_updated_at

                obj.save()

                print("UPDATED SUCCESS")

                print("DB ICON NAME:", obj.icon.name if obj.icon else None)

                if obj.icon:
                    print("DB ICON URL:", obj.icon.url)
                    print("DB ICON PATH:", obj.icon.path)

            # =====================================================
            # CREATE
            # =====================================================

            else:

                print("MODE: CREATE")

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

                print("CREATED SUCCESS")

                print("DB ICON NAME:", obj.icon.name if obj.icon else None)

                if obj.icon:
                    print("DB ICON URL:", obj.icon.url)
                    print("DB ICON PATH:", obj.icon.path)

        except Exception as e:

            print("\nERROR TEMPLATE:")
            print(data)

            print("ERROR:", str(e))

            import traceback

            traceback.print_exc()

    print("\n========== SYNC TEMPLATES END ==========\n")
