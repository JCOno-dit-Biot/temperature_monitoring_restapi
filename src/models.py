
from datetime import datetime
import logging

from pydantic import BaseModel, Field


class room(BaseModel):
    name: str

#should implement upper and lower bounds for temperature and humidity using pydantic
class measurement(BaseModel):
    room: room
    entry_timestamp : datetime
    temperature: float = Field (ge = -40, le = 70)
    humidity: float = Field (ge = 0, le = 1)

    
            
