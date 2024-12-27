from ..Database.requests import *


def find_players(category, category_value):
    cat_type = is_relevat_category(category)
    if cat_type != None and isinstance(category_value, cat_type):
        return find_relevat_players(category, category_value)
    else:
        return False


def add_player_to_bookmarks(player):
    if isinstance(player, Player):
        return not is_player_in_bookmarks(player)
    else:
        return False
