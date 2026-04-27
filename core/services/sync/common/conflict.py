def resolve_update(server_obj, client_data, client_dt, server_dt):
    """
    единая точка конфликта update
    """

    if not client_dt:
        return False  # игнор

    if server_dt >= client_dt:
        return False  # server wins

    return True  # client wins
