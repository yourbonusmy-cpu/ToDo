from django.urls import path

from core.views_new.auth import user_logout, UserLoginView, register
from core.views_new.calendar import calendar_data
from core.views_new.blocks import (
    block_create,
    download_blocks_json_zip,
    download_blocks_xlsx,
    BlockListView,
    delete_block,
    hide_block,
    block_detail,
)
from core.views_new.group_templates import (
    group_templates_page,
    group_template_create_or_edit,
    api_group_templates,
    api_group_template_delete,
)
from core.views_new.home import home
from core.views_new.calendar import calendar_page
from core.views_new.profile import profile_view
from core.views_new.stats import stats_weekdays_page, stats_weekdays_api
from core.views_new.task_templates import (
    task_templates_page,
    task_template_create,
    api_add_all_system_task_templates,
    api_task_template_delete,
    api_add_system_task_template,
    api_task_templates,
    task_template_create_or_edit,
    increment_template_selected,
)
from core.views_new.weather import weather_view

# Home
urlpatterns = [
    path("", home, name="home"),
]

# TaskTemplates
urlpatterns += [
    path("task_templates/create/", task_template_create, name="task_template_create"),
    path("api/task_templates/", api_task_templates, name="api_task_templates"),
    path("task_templates/", task_templates_page, name="task_templates"),
    path("api/system_task_templates/add_all/", api_add_all_system_task_templates),
    path("api/system_task_templates/<int:pk>/add/", api_add_system_task_template),
    path(
        "task_templates/<int:template_id>/edit/",
        task_template_create_or_edit,
        name="task_template_edit",
    ),
    path(
        "api/templates/<int:template_id>/select/",
        increment_template_selected,
        name="template_select",
    ),
    path("api/task_templates/<int:task_template_id>/delete/", api_task_template_delete),
]

# GroupTemplates
urlpatterns += [
    path(
        "group_templates/",
        group_templates_page,
        name="group_templates",
    ),
    path("api/group_templates/", api_group_templates, name="api_group_templates"),
    path(
        "group_templates/create/",
        group_template_create_or_edit,
        name="group_template_create",
    ),
    path(
        "group_templates/<int:group_id>/edit/",
        group_template_create_or_edit,
        name="group_template_edit",
    ),
    path(
        "api/group_templates/<int:group_id>/delete/",
        api_group_template_delete,
        name="api_group_template_delete",
    ),
]

# Blocks
urlpatterns += [
    path("block/create/", block_create, name="block_create"),
    path("api/blocks/", BlockListView.as_view(), name="api_blocks"),
    path("block/<int:block_id>/view/", block_detail, name="block_detail"),
    path("block/<int:block_id>/edit/", block_create, name="block_edit"),
    path("api/block/<int:block_id>/hide/", hide_block, name="api_hide_block"),
    path("api/block/<int:block_id>/delete/", delete_block, name="api_delete_block"),
    path(
        "download/json_zip/",
        download_blocks_json_zip,
        name="download_blocks_json_zip",
    ),
    path("download/xlsx/", download_blocks_xlsx, name="download_blocks_xlsx"),
]

# Calendar
urlpatterns += [
    path("calendar/", calendar_page, name="calendar"),
    path("api/calendar/", calendar_data, name="calendar_data"),
]

# Weather
urlpatterns += [
    path("weather/", weather_view, name="weather"),
]

# Stats
urlpatterns += [
    path("stats/weekdays/", stats_weekdays_page, name="stats_weekdays"),
    path("api/statistics/", stats_weekdays_api, name="stats_weekdays_api"),
]

# Profile
urlpatterns += [
    path("profile/", profile_view, name="profile"),
]

# Auth
urlpatterns += [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", register, name="register"),
    path("logout/", user_logout, name="logout"),
]
