
from datetime import datetime
import logging

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Room(SQLModel, table = True):
    __tablename__ = "room"
    id : int = Field (default = None, primary_key=True)
    name: str = Field(unique=True)
    sensor: List[Optional["Sensor"]] = Relationship(back_populates="room")
    plant: List[Optional["Plant"]] = Relationship(back_populates="room")

class Plant(SQLModel, table=True):
    __tablename__ = "plant"
    id: int = Field (default = None, primary_key=True)
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    room: Optional[Room] = Relationship(back_populates="plant")
    name: str = Field(unique=True)
    sensor: Optional["PlantSensor"] = Relationship(back_populates="plant")

class Sensor(SQLModel, table = True):
    __tablename__ = "sensor"
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    room: Optional[Room] = Relationship(back_populates="sensor")
    serial_number: int = Field(default = 0, primary_key=True)
    humidity_temperature_entry: Optional[List["HumityTemperatureEntry"]]= Relationship(back_populates = "sensor")

class PlantSensor(SQLModel, table = True):
    __tablename__ = "plant_sensor"
    plant_id: int = Field(default=None, foreign_key="plant.id")
    plant: Plant = Relationship(back_populates="sensor")
    serial_number: int = Field(default = 0, primary_key=True)
    plant_sensor_entry: Optional[List["PlantSensorEntry"]]= Relationship(back_populates = "sensor")
  

class HumityTemperatureEntry(SQLModel, table = True):
    __tablename__ = "humidity_temperature_entry"
    sensor_id: int = Field(default=0, foreign_key="sensor.serial_number", primary_key=True)
    sensor: Optional[Sensor] = Relationship(back_populates="humidity_temperature_entry")
    entry_timestamp : datetime = Field (primary_key=True)
    temperature: float = Field (ge = -40, le = 70)
    humidity: float = Field (ge = 0, le = 1)

class PlantSensorEntry(SQLModel, table = True):
    __tablename__ = "plant_sensor_entry"
    sensor_id: int = Field(default=0, foreign_key="plant_sensor.serial_number", primary_key=True)
    sensor: Optional[PlantSensor] = Relationship(back_populates="plant_sensor_entry")
    entry_timestamp : datetime = Field (primary_key=True)
    temperature: float = Field (ge = -40, le = 70)
    humidity: float = Field (ge = 0, le = 1)
    wetness: float = Field (ge = 0, le = 1)
            
