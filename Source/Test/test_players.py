from ..Interfaces.players import *
from ..Database.mock_data import Player
import pytest

@pytest.mark.parametrize('player, expected_result',
                         [(Player("Petya", "Polyakov", "Real", 54, date(1991, 5, 23), 165, 80, False, 'left'), False),
                          (Player("Zhenya", "Polyakov", "Real", 53, date(1991, 5, 23), 165, 80, False, 'left'), True),
                          ("Zhenya", False) #broken type
                          ])
def test_sign_in_scout(player, expected_result):
    assert add_player_to_bookmarks(player) == expected_result

@pytest.mark.parametrize('category, category_value, expected_result',
                         [('name', 'Valera', Player("Valera", "Semyonov", "Barca", 54, date(1978, 11, 3), 178, 72, True, 'right')),
                          ('name', 'Petya', None),
                          ('name', 124, False),
                          
                          ('surname', 'Slonov', Player("Zhenya", "Slonov", "Celta", 22, date(2000, 8, 22), 166, 64, True, 'right', 18)),
                          ('surname', 'Syomin', None),
                          ('surname', False, False),
                          
                          ('age', 22, None),
                          ('age', 'Petya', False),
                          
                          ('birth_date', date(2002, 3, 11), Player("Kirill", "Smirnov", "Barca", 54, date(2002, 3, 11), 170, 80, False, 'right')),
                          ('birth_date', '2002.03.11', False),
                          ('birth_date', date(2003, 3, 22), None),
                          
                          ('height', 171.5, Player("Petr", "Kozlov", "Sevilia", 31, date(1999, 2, 16), 171.5, 70, True, 'right')),
                          ('height', 160.25, None),
                          ('height', '1000', False),
                          
                          ('weight', 64, None),
                          ('weight', '75.25', False),
                          
                          ('health_status', False, Player("Kirill", "Smirnov", "Barca", 54, date(2002, 3, 11), 170, 80, False, 'right')),
                          ('health_status', True, None),
                          ('health_status', 160.25, False),
                          
                          ('leading_foot', 'right', Player("Valera", "Semyonov", "Barca", 54, date(1978, 11, 3), 178, 72, True, 'right')),
                          ('leading_foot', 'both', None),
                          ('leading_foot', 1, False),
                          
                          ('goals_in_season', 33, Player("Lionel", "Messi", "Barca", 33, date(1985, 11, 3), 150, 56, True, 'both')),
                          ('goals_in_season', 16, None),
                          ('goals_in_season', '1000', False)])
def test_find_players(category, category_value, expected_result):
    assert find_players(category, category_value) == expected_result

    
