# pagination.py
from rest_framework.pagination import CursorPagination


class BlockCursorPagination(CursorPagination):
    page_size = 10
    ordering = ("-created_at", "-id")  # важно!
