from ..Interfaces.club_personal_acc import *
import pytest

@pytest.mark.parametrize('name, surname, age, birth_data, height, \
                         weight, health_status, leading_foot, expected_result',
                         [('Igor', 'Igor', 10, date(2012, 6, 13), 175, 65, True, 'right', True),
                          (True, 'Igor', 10, date(2012, 6, 13), 175, 65, True, 'right', False),
                          ('Igor', [1, 2], '152', date(2012, 6, 13), 175, 65, True, 'right', False),
                          ('Igor', 'Igor', 10, date(1889, 6, 7), 175, 65, True, 'right', False),
                          ('Igor', 'Igor', 10, date(2012, 6, 13), '175', 65, True, 'right', False),
                          ('Igor', 'Igor', 10, date(2012, 6, 13), 175, (65, 11), True, 'right', False),
                          ('Igor', 'Igor', 10, date(2012, 6, 13), 175, 65, 'True', 'right', False),
                          ('Igor', 'Igor', 10, date(2012, 6, 13), 175, 65, True, 2, False)])
def test_add_player(name, surname, age, birth_data, height, \
                         weight, health_status, leading_foot, expected_result):
    assert add_player(name, surname, age, birth_data, height, \
                         weight, health_status, leading_foot) == expected_result

@pytest.mark.parametrize('name, surname, info_type, new_info, expected_result',
                         [('Valera', 'Semyonov', 'health_status', False, True),
                          ('Valera', 'Semyonov', 'height', 181, True),
                          ('Valera', 'Semyonov', 'health_status', 'yes', False),
                          ('Igor', 'Semyonov', 'health_status', False, False),
                          ('', 'Semyonov', 'health_status', False, False),
                          #('Valera', 'Semyonov', 'weight', True, False)
                          ])
def test_change_player_info(name: str, surname: str, info_type: str, new_info, expected_result):
    assert change_player_info(name, surname, info_type, new_info) == expected_result
    
@pytest.mark.parametrize('name, surname, club, expected_result',
                         [('Valera', 'Semyonov', 'Barca', True),
                          ('', 'Semyonov', 'Barca', False),
                          ('Valera', 2, 'Barca', False)])    
def test_delete_player(name: str, surname: str, club: str, expected_result):
    assert delete_player(name, surname, club) == expected_result

    
    