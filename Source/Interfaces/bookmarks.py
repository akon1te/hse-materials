from ..Database.requests import *


def update_players():
    return is_all_players_able()


def delete_from_bookmarks(players_idx):
    origin_len = get_bookmarks_len()
    for idx in players_idx:
        if not isinstance(idx, int) or idx > origin_len or idx < 0:
            return (False, idx)
    return is_albe_to_delete(players_idx)


def request_info(player_idx):
    origin_len = get_bookmarks_len()
    if not isinstance(player_idx, int) or player_idx > origin_len or player_idx <= 0:
        return (False, player_idx)

    return (True, is_info_able(player_idx))
