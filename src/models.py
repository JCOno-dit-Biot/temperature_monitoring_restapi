
from datetime import datetime
import logging

from pydantic import BaseModel


class room(BaseModel):
    name: str


class measurement(BaseModel):
    room: room
    entry_timestamp : datetime
    temperature: float
    humidity: float

    
            
