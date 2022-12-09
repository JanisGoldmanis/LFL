class Warning:
    def __init__(self, Time="", Nr=-1):
        self.Time = Time
        self.Nr = Nr

    def __str__(self):
        return f"Penalty time: {self.Time} Player: {self.Nr}"
