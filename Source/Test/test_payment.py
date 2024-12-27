from ..Interfaces.payment import *
import pytest

@pytest.mark.parametrize('expected_result',
                         [(23)])
def test_check_remaining_time(expected_result):
    assert check_remaining_time() == expected_result

    
@pytest.mark.parametrize('bank_acc, password, payment, expected_result',
                         [(123456789, 'normal_pasw', 1000, 'Done'),
                          (135790009, 'qwerty', 500.5, 'Done'),
                          (123456789, 'normal_password', 1000, 'wrong data'),
                          (123456780, 'normal_pasw', 1000, 'wrong data'),
                          (544554450, 'old_man', 654, 'not enough money'),
                          (123456789, 'normal_pasw', 10001, 'not enough money'),
                          ('123456789', 'normal_pasw', 654, False),
                          (135790009, 'qwerty', '1', False)])
def test_pay(bank_acc, password, payment, expected_result):
    assert pay(bank_acc, password, payment) == expected_result
    