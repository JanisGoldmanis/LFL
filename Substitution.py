class Substitution:
    def __init__(self, time="", Nr1 = -1, Nr2 = -1):
        self.time = time
        self.Nr1 = Nr1
        self.Nr2 = Nr2

    def __str__(self):
        return "Substitution time: "+self.time+" Leaving: "+str(self.Nr1)+" Coming: "+str(self.Nr2)
