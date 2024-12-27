from ..Database.requests import *

def check_remaining_time():
    rt = get_remaining_time()
    if rt == -1:
        return False
    else:
        return rt
    
def pay(bank_acc, password, payment):
    if isinstance(bank_acc, int) and isinstance(password, str) and isinstance(payment, (int, float)):
        ans = is_relevant_bank_acc(bank_acc, password, payment)
        if ans == -1:
            return 'wrong data'
        if ans == -2:
            return 'not enough money'
        if ans == 0:
            return 'Done'
    else:
        return False