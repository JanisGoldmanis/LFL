class Player:
    def __init__(self, name="", surname="", role="", number=0):
        self.name = name
        self.surname = surname
        self.role = role
        self.number = number

    def __str__(self):
        return self.surname + ", " + self.name
