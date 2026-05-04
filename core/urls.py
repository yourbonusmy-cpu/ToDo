from django.urls import path

from core.models import TaskTemplate
from core.views.api_blocks import (
    create_block,
    get_block,
    update_block,
    hide_block,
    BlockListView,
)
from core.views.api_stats import stats_weekdays_api
from core.views.api_templates import api_templates, TaskTemplateListView
from core.views.api_weather import weather_api
from core.views.auth import (
    UserLoginView,
    register,
    user_logout,
    CustomTokenObtainPairView,
)
from core.views.blocks import (
    delete_block,
    decrypt_task,
    block_create,
)
from core.views.group_templates import (
    group_template_create_or_edit,
    group_templates_list,
    api_group_detail,
    api_group_templates,
    api_group_template_delete,
    GroupTemplateListView,
)
from core.views.home import (
    home,
    block_detail,
    download_blocks_json_zip,
    download_blocks_xlsx,
)
from core.views.pin import lock_pin, unlock_pin, pin_unlock_page
from core.views.stats import stats_weekdays_page
from core.views.task_templates import (
    task_template_create_view,
    template_create,
    add_system_template_ajax,
    template_create_or_edit,
    template_delete,
    templates_page,
    add_all_system_templates,
    increment_template_selected,
    api_template_delete,
    api_add_system_template,
    api_add_all_system_templates,
    api_system_task_templates,
)

from core.views.tasks import task_template_create
from core.views.weather import weather_view
from core.views.api import calendar_data

from core.views.profile import (
    profile_view,
    change_password_view,
    delete_account_view,
    toggle_pin_view,
    change_pin_view,
    verify_pin,
    set_pin,
    disable_pin,
)

from django.shortcuts import render

from core.views_new.calendar import calendar_page

# other
urlpatterns = [
    path("api/weather/", weather_api, name="api_weather"),
    path("api/statistics/", stats_weekdays_api, name="stats_weekdays_api"),
    path("stats/weekdays/", stats_weekdays_page, name="stats_weekdays"),
    path("decrypt-task/", decrypt_task, name="decrypt_task"),
    path("lock-pin/", lock_pin, name="lock_pin"),
    path("unlock-pin/", unlock_pin, name="unlock_pin"),
    path("pin-unlock/", pin_unlock_page, name="pin_unlock"),
]

# groups
urlpatterns += [
    path("api/groups_new/", GroupTemplateListView.as_view()),
    path(
        "api/group_templates/<int:group_id>/",
        api_group_detail,
        name="api_group_detail",
    ),
]

# login
urlpatterns += []

# block
urlpatterns += [
    path("api/block/<int:block_id>/", get_block, name="api_get_block"),
    path("api/block/<int:block_id>/update/", update_block, name="api_update_block"),
    path("block/create/", block_create, name="block_create"),
    path("api/block/create/", create_block, name="api_create_block"),
    # path("api/blocks/", api_blocks, name="api_blocks"),
    # path("api/blocks/json/", api_blocks_json, name="api_blocks_json"),
]

# profile
urlpatterns += [
    path("profile/", profile_view, name="profile"),
    path("profile/change-password/", change_password_view, name="change_password"),
    path("profile/delete/", delete_account_view, name="delete_account"),
    path("profile/toggle-pin/", toggle_pin_view, name="toggle_pin"),
    path("profile/change-pin/", change_pin_view, name="change_pin"),
    path("profile/verify-pin/", verify_pin, name="verify_pin"),
    path("profile/set-pin/", set_pin, name="set_pin"),
    path("profile/disable-pin/", disable_pin, name="disable_pin"),
]

# templates
urlpatterns += [
    path(
        "api/system-task-templates/",
        api_system_task_templates,
        name="api_system_task_templates",
    ),
    path("api/templates/", api_templates, name="api_templates"),
    path("task-template/create/", task_template_create, name="task_template_create"),
    path(
        "templates/system/add_all/",
        add_all_system_templates,
        name="add_all_system_templates",
    ),
    path(
        "templates/system/<int:pk>/add/",
        add_system_template_ajax,
        name="add_system_template_ajax",
    ),
    path(
        "templates/<int:template_id>/edit/",
        template_create_or_edit,
        name="template_edit",
    ),
    path(
        "templates/<int:template_id>/delete/", template_delete, name="template_delete"
    ),
    path(
        "task-template/create/", task_template_create_view, name="task_template_create"
    ),
    path(
        "api/templates/<int:template_id>/select/",
        increment_template_selected,
        name="template_select",
    ),
]
