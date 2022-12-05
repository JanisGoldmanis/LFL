class Team:
    def __init__(self, name="", players=[], starting=[], goals=[], substitutions=[], warnings=[]):
        self.name = name
        self.players = players
        self.starting = starting
        self.goals = goals
        self.substitutions = substitutions
        self.warnings = warnings

    def __str__(self):
        return self.name
