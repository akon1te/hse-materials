from datetime import date


# MOK данные из бд по запросу для тестирования
class Scout:
    def __init__(self):
        self.login = "Boba"
        self.password = "qwerty"
        self.name = "Zhenya"
        self.surname = "Ivanov"
        self.job_club = "Real"


class Club:
    def __init__(self):
        self.registration_number = 5445
        self.name = "Barca"
        self.password = "aboba"


class Player:
    def __init__(
        self,
        name,
        surname,
        club,
        age,
        birth_data,
        height,
        weight,
        health_status,
        lead_f,
        goals_in_season=None,
    ):
        self.name = name
        self.surname = surname
        self.club = club
        self.age = age
        self.birth_data = birth_data
        self.height = height
        self.weight = weight
        self.health_status = health_status
        self.leading_foot = lead_f
        self.goals_in_season = goals_in_season

    def __eq__(self, other_player):
        return (
            self.name == other_player.name
            and self.surname == other_player.surname
            and self.club == other_player.club
            and self.age == other_player.age
            and self.birth_data == other_player.birth_data
            and self.height == other_player.height
            and self.weight == other_player.weight
            and self.health_status == other_player.health_status
            and self.leading_foot == other_player.leading_foot
        )


bookmark_players = [
    (1, Player(
        "Valera", "Semyonov", "Barca", 54, date(1978, 11, 3), 178, 72, True, "right"
    )),
    (1, Player(
        "Dima", "Sidorov", "Barca", 32, date(2000, 8, 16), 190, 90, True, "right"
    )),
    (1, Player(
        "Petya", "Polyakov", "Real", 54, date(1991, 5, 23), 165, 80, False, "left"
    )),
    (0, Player(
        "Sergey", "Sergeyev", "Real", 17, date(2012, 12, 8), 163, 65, True, "left", 12
    ))
]

scout = Scout()
club = Club()
player = Player(
    "Valera", "Semyonov", "Barca", 54, date(1978, 11, 3), 178, 72, True, "right"
)
CHECK_DATE = date(1900, 12, 31)
RELEVATN_BANK_ACC = [(123456789, 'normal_pasw', 10000), (544554450, 'old_man', 54), (135790009, 'qwerty', 653)]