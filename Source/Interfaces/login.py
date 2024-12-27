from ..Database.requests import *
    
def sign_in_scout(login: str, password: str):
    
    return is_real_user(login, password)

def sign_in_club(login: int, password: int):
    
    return is_real_club(login, password)

def sign_up_club(registration_number: int, password: str):
    
    if not isinstance(password, str) or not isinstance(registration_number, int):
        return False
    else:
        return True

    
    


    
    