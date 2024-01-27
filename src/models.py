from dataclasses import dataclass
from datetime import datetime
import logging



class room():

    def __init__(self, name):
        self.name = name

@dataclass
class measurement:
    room: room
    entry_timestamp : datetime
    temperature: float
    humidity: float

    
            
