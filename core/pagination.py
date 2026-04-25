# pagination.py
from rest_framework.pagination import CursorPagination


class BlockCursorPagination(CursorPagination):
    page_size = 15
    page_size_query_param = "page_size"  # 👈 ключ
    max_page_size = 50  # 👈 защита от перегрузки
    ordering = ("-created_at", "-id")  # важно!


class GroupCursorPagination(CursorPagination):
    page_size = 15
    page_size_query_param = "page_size"  # 👈 ключ
    max_page_size = 50  # 👈 защита от перегрузки
    ordering = "-updated_at"


class TemplateCursorPagination(CursorPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-updated_at"
