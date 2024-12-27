from ..Interfaces.scout_personal_acc import *
import pytest

@pytest.mark.parametrize('info_type, new_info, expected_result',
                         [('password', '544554', True),
                          ('password', 544554, False),
                          ('password', '', False),
                          ('job_club', 'Atletic', True),
                          ('job_club', 1234, False),
                          ('job_club', 'Real', False),
                          ('job_club', '', False),
                          ('name', '3321', False)])
def test_change_my_info(info_type, new_info, expected_result):
    assert change_my_info(info_type, new_info) == expected_result