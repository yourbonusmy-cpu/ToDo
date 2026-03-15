from django.urls import path

from core.views.api_blocks import (
    create_block,
    load_blocks,
    get_block,
    update_block,
    hide_block,
)
from core.views.auth import UserLoginView, register, user_logout
from core.views.blocks import block_builder, delete_block, decrypt_task
from core.views.group_templates import (
    group_template_create_or_edit,
    group_template_delete,
    group_templates_list,
    api_group_detail,
)
from core.views.home import home, block_detail
from core.views.task_templates import (
    task_template_create_view,
    template_create,
    add_system_template_ajax,
    template_create_or_edit,
    template_delete,
    templates_page,
    add_all_system_templates,
)

from core.views.tasks import task_template_create

urlpatterns = [
    path("decrypt-task/", decrypt_task, name="decrypt_task"),
    path("block/<int:block_id>/view/", block_detail, name="block_detail"),
    path("api/block/<int:block_id>/delete/", delete_block, name="api_delete_block"),
    path("api/block/<int:block_id>/hide/", hide_block, name="api_hide_block"),
    path("api/block/<int:block_id>/", get_block, name="api_get_block"),
    path("api/block/<int:block_id>/update/", update_block, name="api_update_block"),
    path("block/create/", block_builder, name="block_builder"),
    path("api/block/create/", create_block, name="api_create_block"),
    path("block/<int:block_id>/edit/", block_builder, name="block_edit"),
    path("api/blocks/", load_blocks, name="api_blocks"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", register, name="register"),
    path("logout/", user_logout, name="logout"),
    path("", home, name="home"),
]

urlpatterns += [
    path("templates/", templates_page, name="templates"),
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
    path("templates/create/", template_create, name="template_create"),
    path(
        "task-template/create/", task_template_create_view, name="task_template_create"
    ),
]


urlpatterns += [
    path(
        "group-templates/",
        group_templates_list,
        name="group_templates",
    ),
    path(
        "group-templates/create/",
        group_template_create_or_edit,
        name="group_template_create",
    ),
    path(
        "group-templates/<int:group_id>/edit/",
        group_template_create_or_edit,
        name="group_template_edit",
    ),
    path(
        "group-templates/<int:group_id>/delete/",
        group_template_delete,
        name="group_template_delete",
    ),
    path(
        "api/groups/<int:group_id>/",
        api_group_detail,
        name="api_group_detail",
    ),
]
