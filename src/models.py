
from datetime import datetime
import logging

from pydantic import BaseModel


class room(BaseModel):
    name: str

#should implement upper and lower bounds for temperature and humidity using pydantic
class measurement(BaseModel):
    room: room
    entry_timestamp : datetime
    temperature: float
    humidity: float

    
            
