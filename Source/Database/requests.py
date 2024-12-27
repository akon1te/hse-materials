from datetime import date
from ..Database.mock_data import scout, Player, player, club, CHECK_DATE, RELEVATN_BANK_ACC, bookmark_players

# Все request подразумевают под собой запросы в базу данных


# login page requests
def is_real_user(login: str, password: str):
    if login == scout.login and password == scout.password:
        return True
    else:
        return False


def is_real_club(registration_number: str, password: str):
    if registration_number == club.registration_number and password == club.password:
        return True
    else:
        return False


# club personal acc requests
def is_real_player(name: str, surname: str, club: str):
    if name == player.name and surname == player.surname and club == player.club:
        return True
    else:
        return False


def is_relevant_info_type(info_type: str):
    if info_type in ["height", "weight", "health_status", "leading_foot"]:
        return True
    else:
        return False


def is_good_date(birth_date: date):
    if birth_date > CHECK_DATE:
        return True
    else:
        return False


# scout personal acc requests
def is_relevant_scout_info_type(info_type):
    if info_type in ["password", "job_club"]:
        return True
    else:
        return False


def is_current_password(new_pass):
    if new_pass != scout.password and new_pass != "":
        return True
    else:
        return False


def is_current_club(new_club):
    if new_club != scout.job_club and new_club != "":
        return True
    else:
        return False


# players page requests
def is_player_in_bookmarks(player):
    bookmark_player = Player("Petya", "Polyakov", "Real", 54, date(1991, 5, 23), 165, 80, False, 'left')
    return player == bookmark_player


def is_relevat_category(category):
    if category == 'name':
        return str
    elif category == 'surname':
        return str
    elif category == 'age':
        return int
    elif category == 'birth_date':
        return date
    elif category == 'height':
        return (int, float)
    elif category == 'weight':
        return (int, float)
    elif category == 'health_status':
        return bool
    elif category == 'leading_foot':
        return str
    elif category == 'goals_in_season':
        return int
    else:
        return None
    
def find_relevat_players(category, category_value):
    if category == 'name':
        if category_value == 'Valera':
            return Player("Valera", "Semyonov", "Barca", 54, date(1978, 11, 3), 178, 72, True, 'right')
        else:
            return None
        
    if category == 'surname':
        if category_value == 'Slonov':
            return Player("Zhenya", "Slonov", "Celta", 22, date(2000, 8, 22), 166, 64, True, 'right')
        else:
            return None
    
    if category == 'age':
        return None
        
        
    if category == 'birth_date':
        if category_value == date(2002, 3, 11):
            return Player("Kirill", "Smirnov", "Barca", 54, date(2002, 3, 11), 170, 80, False, 'right')
        else:
            return None
    
    if category == 'height':
        if category_value == 171.5:
            return Player("Petr", "Kozlov", "Sevilia", 31, date(1999, 2, 16), 171.5, 70, True, 'right')
        else:
            return None
        
    if category == 'weight':
        return None

    if category == 'health_status':
        if category_value == False:
            return Player("Kirill", "Smirnov", "Barca", 54, date(2002, 3, 11), 170, 80, False, 'right')
        else:
            return None

    if category == 'leading_foot':
        if category_value == 'right':
            return Player("Valera", "Semyonov", "Barca", 54, date(1978, 11, 3), 178, 72, True, 'right')
        else:
            return None
        
    if category == 'goals_in_season':
        if category_value == 33:
            return Player("Lionel", "Messi", "Barca", 33, date(1985, 11, 3), 150, 56, True, 'both', 22)
        else:
            return None


#bookmarks requests
def get_bookmarks_len():
    return len(bookmark_players)

def is_all_players_able():
    origin_len = len(bookmark_players)
    for pl in bookmark_players:
        if pl[0] == 0:
            origin_len -= 1
            
    return origin_len 

def is_albe_to_delete(idxs):
    origin_len = len(bookmark_players)
    for i in idxs:
        origin_len -= 1
    return (True, origin_len)

def is_info_able(idx):
    if idx in [1, 3]:
        return None
    else:
        return 'link to phone and email'
    
    
#payment request
def is_relevant_bank_acc(bank_acc, password, payment):
    for ba in RELEVATN_BANK_ACC:
        if bank_acc == ba[0] and password == ba[1]:
            if ba[2] >= payment:
                return 0
            else:
                return -2
    return -1
        
def get_remaining_time():
    return 23   