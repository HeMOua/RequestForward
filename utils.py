from setting import TITLE, VERSION, AUTHOR


def get_app_info(is_editing: bool = False):
    if is_editing:
        return f"{TITLE} v{VERSION} by {AUTHOR} - 未保存"
    else:
        return f"{TITLE} v{VERSION} by {AUTHOR}"
