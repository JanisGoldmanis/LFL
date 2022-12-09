class Game:
    def __init__(self, date="0000/00/00", spectators=0, place="", referees=[], teams=[], head_referee = ""):
        self.place = place
        self.spectators = spectators
        self.date = date
        self.referees = referees
        self.teams = teams
        self.head_referee = head_referee

    def __str__(self):
        return "Place: " + self.place + " Spectators: " + str(self.spectators) + " Date: " + self.date
