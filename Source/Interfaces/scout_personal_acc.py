from ..Database.requests import *
from datetime import date


def change_my_info(info_type: str, new_info):
    if is_relevant_scout_info_type(info_type) == False:
        return False

    if (
        info_type == "password"
        and isinstance(new_info, str)
        and is_current_password(new_info)
    ):
        return True

    if (
        info_type == "job_club"
        and isinstance(new_info, str)
        and is_current_club(new_info)
    ):
        return True

    return False
