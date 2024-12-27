from ..Interfaces.login import *
import pytest

@pytest.mark.parametrize('name, password, expected_result',
                         [('Boba', 'qwerty', True),
                          (124, 'qwerty', False),
                          ('Boba', 'qwertyAB', False),
                          ('Biba', 'qwerty', False),
                          ('Boba', '', False),
                          ('', 'qwerty', False)])
def test_sign_in_scout(name, password, expected_result):
    assert sign_in_scout(name, password) == expected_result

@pytest.mark.parametrize('name, password, expected_result',
                         [(5445, 'aboba', True),
                          (5445, 'abiba', False),
                          ('5445', 'aboba', False),
                          (5445, 124, False),
                          ('', 'qwerty', False),
                          ('5445', '', False)])
def test_sign_in_club(name, password, expected_result):
    assert sign_in_club(name, password) == expected_result
    
@pytest.mark.parametrize('registration_number, password, expected_result',
                         [(5445, 'aboba', True),
                          (5445, 'abiba', False),
                          ('5445', 'aboba', False),
                          (5445, 124, False),
                          ('', 'qwerty', False),
                          ('5445', '', False)])    
def test_sign_up(registration_number, password, expected_result):
    assert sign_in_club(registration_number, password) == expected_result

    
    