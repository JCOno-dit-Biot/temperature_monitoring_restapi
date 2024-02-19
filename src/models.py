
from datetime import datetime
import logging

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class room(SQLModel, Table = True):
    id : int = Field (default = None, primary_key=True)
    name: str

class sensor(SQLModel, Table = True):
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    room: Optional[room] = Relationship(back_populates="user")
    serial_number: int = Field(default = 0, primary_key=True)
    type: str


class humity_temperature_entry(SQLModel, Table = True):
    sensor_id: int = Field(default=0, foreign_key="sensor.serial_number")
    sensor: Optional[sensor] = Relationship(back_populates="sensor")
    entry_timestamp : datetime
    temperature: float = Field (ge = -40, le = 70)
    humidity: float = Field (ge = 0, le = 1)

class wetness_entry(SQLModel, Table = True):
    sensor_id: int = Field(default=0, foreign_key="sensor.serial_number")
    sensor: Optional[sensor] = Relationship(back_populates="sensor")
    entry_timestamp : datetime
    wetness: float = Field (ge = 0, le = 1)
            
