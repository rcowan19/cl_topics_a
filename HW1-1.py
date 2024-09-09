class Time:
    def __init__(self, race_time):
        self.minutes, self.seconds = [float(t) for t in race_time.split(":")]
        self.time = self.minutes * 60 + self.seconds
    def __str__(self):
        return f"{int(self.minutes):02}:{self.seconds:05.2f}"
    def __eq__(self,other):
        if self.time == other.time:
            return True
        else:
            return False
    def __ne__(self,other):
        if self.time != other.time:
            return True
        else:
            return False
    def __lt__(self,other):
        if self.time < other.time:
            return True
        else:
            return False
    def __gt__(self,other):
        if self.time > other.time:
            return True
        else:
            return False
    def __le__(self,other):
        if self.time <= other.time:
            return True
        else:
            return False
    def __ge__(self,other):
        if self.time >= other.time:
            return True
        else:
            return False
   
class Athlete:
    def __init__(self, name, team, place, time):
        self.name = name
        self.team = team
        self.place = place
        self.time = Time(time)
    
    def __str__(self):
        return (f"Athlete: {self.name}, Team: {self.team}, Place: {self.place}, "f"Time: {self.time}")
    
    def __eq__(self,other):
        if self.place == other.place:
            return True
        else:
            return False
    def __ne__(self,other):
        if self.place != other.place:
            return True
        else:
            return False
    def __lt__(self,other):
        if self.place < other.place:
            return True
        else:
            return False
    def __gt__(self,other):
        if self.place > other.place:
            return True
        else:
            return False
    def __le__(self,other):
        if self.place <= other.place:
            return True
        else:
            return False
    def __ge__(self,other):
        if self.place >= other.place:
            return True
        else:
            return False

athlete1 = Athlete("John Doe", "Team A", 1, "05:32.40")
athlete2 = Athlete("Jane Smith", "Team B", 2, "05:31.15")
print(athlete1)  # Output: Athlete: John Doe, Team: Team A, Place: 1, Time: 05:32.47
print(athlete2)  # Output: Athlete: Jane Smith, Team: Team B, Place: 2, Time: 05:31.15
print(athlete1 < athlete2)  # Output: True