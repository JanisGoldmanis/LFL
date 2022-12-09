class Goals:
    def __init__(self, time="", passers=[], scorer=-1, type=""):
        self.time = time
        self.passers = passers
        self.scorer = scorer
        self.type = type

    def __str__(self):
        return f"{self.time} scorer {self.scorer} passers: {self.passers} type: {self.type}"
