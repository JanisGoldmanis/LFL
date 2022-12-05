class Referee:
    def __init__(self, surname="", name=""):
        self.Surname = surname
        self.Name = name

    def __str__(self):
        return self.Surname + ", " + self.Name


