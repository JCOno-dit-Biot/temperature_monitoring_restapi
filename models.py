from dataclasses import dataclass
from datetime import datetime

class room():

    def __init__(self, name):
        self.name = name

dataclass()
class measurement():
    timestamp : datetime
    temperature: float
    humidity: float

