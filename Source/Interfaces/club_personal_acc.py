from ..Database.requests import *
from datetime import date

# Допустим мы зашли по аккаунтом этого клуба
YOUR_CLUB = "Barca"


def add_player(
    name: str,
    surname: str,
    age: int,
    birth_data: date,
    height: int,
    weight: int,
    health_status: bool,
    leading_foot: str,
):
    if (
        not isinstance(name, str)
        or not isinstance(surname, str)
        or not isinstance(age, int)
        or not isinstance(birth_data, date)
        or not isinstance(height, (int, float))
        or not isinstance(weight, (int, float))
        or not isinstance(health_status, bool)
        or not isinstance(leading_foot, str)
    ):
        return False

    return is_good_date(birth_data)


def change_player_info(name: str, surname: str, info_type: str, new_info):
    if (
        is_real_player(name, surname, YOUR_CLUB) == False
        or is_relevant_info_type(info_type) == False
    ):
        return False

    if (
        (info_type == "height" and not isinstance(new_info, (int, float)))
        or (info_type == "weight" and not isinstance(new_info, (int, float)))
        or (info_type == "health_status" and not isinstance(new_info, bool))
        or (info_type == "leading_foot" and not isinstance(new_info, str))
    ):
        return False

    return True


def delete_player(name: str, surname: str, club: str):
    if is_real_player(name, surname, club):
        return True
    else:
        return False
