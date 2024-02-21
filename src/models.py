
from datetime import datetime
import logging

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Room(SQLModel, table = True):
    __tablename__ = "room"
    id : int = Field (default = None, primary_key=True)
    name: str
    sensor: Optional["Sensor"] = Relationship(back_populates="room")

class Sensor(SQLModel, table = True):
    __tablename__ = "sensor"
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    room: Optional[Room] = Relationship(back_populates="sensor")
    serial_number: int = Field(default = 0, primary_key=True)
    type: str
    humidity_temperature_entry: Optional["HumityTemperatureEntry"]= Relationship(back_populates = "sensor")
    wetness_entry: Optional["WetnessEntry"]= Relationship(back_populates = "sensor")

class HumityTemperatureEntry(SQLModel, table = True):
    __tablename__ = "humidity_temperature_entry"
    sensor_id: int = Field(default=0, foreign_key="sensor.serial_number", primary_key=True)
    sensor: Optional[Sensor] = Relationship(back_populates="humidity_temperature_entry")
    entry_timestamp : datetime = Field (primary_key=True)
    temperature: float = Field (ge = -40, le = 70)
    humidity: float = Field (ge = 0, le = 1)

class WetnessEntry(SQLModel, table = True):
    __tablename__ = "wetness_entry"
    sensor_id: int = Field(default=0, foreign_key="sensor.serial_number", primary_key=True)
    sensor: Optional[Sensor] = Relationship(back_populates="wetness_entry")
    entry_timestamp : datetime = Field (primary_key=True)
    wetness: float = Field (ge = 0, le = 1)
            
