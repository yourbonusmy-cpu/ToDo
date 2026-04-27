from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware


def safe_parse_dt(value):
    if not value:
        return None

    dt = parse_datetime(value)
    if not dt:
        return None

    if not is_aware(dt):
        dt = make_aware(dt)

    return dt


def is_newer(server_dt, client_dt):
    if not client_dt:
        return True
    return server_dt < client_dt
