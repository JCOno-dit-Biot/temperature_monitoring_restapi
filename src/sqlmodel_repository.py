from sqlmodel import create_engine, Session, select, func
from sqlalchemy.orm import joinedload

from src.models import Room
from .models import *
from .abstract_repository import AbstractRepository
from typing import Union

logger = logging.getLogger(__name__)


class SQLModel_repository(AbstractRepository):

    def __init__(self, engine):
        self.engine = engine
    
    def add_room(self,room: Room):
        with Session(self.engine) as session:
            try:
                session.add(room)

            except Exception as e:
                session.rollback()
                logger.error('could not insert new room in database')
                logger.error(e)
            else:
                session.commit()
                session.refresh(room)

            return room
        
    def add_plant(self, plant):
        with Session(self.engine) as session:
            try:
                session.add(plant)

            except Exception as e:
                session.rollback()
                logger.error('could not insert new room in database')
                logger.error(e)
            else:
                session.commit()
                session.refresh(plant)

            return plant

        
    def get_room(self, room: Room):

        with Session(self.engine) as session:
            statement = select(Room).where(func.lower(Room.name) == room.name.lower())
            room = session.exec(statement).first()
        return room
    
    def get_plant(self, plant: Plant):
        with Session(self.engine) as session:
            statement = select(Plant).where(func.lower(Plant.name) == plant.name.lower())
            plant = session.exec(statement).first()
        return plant
    
    def add_sensor(self, sensor: Union[Sensor, PlantSensor]):

        with Session(self.engine) as session:
            try:
                session.add(sensor)
            except Exception as e:
                session.rollback()
                logger.error(f'could not insert new sensor {sensor.serial_number} in database')
                logger.error(e)
            else:
                session.commit()
                session.refresh(sensor)

        return sensor
    
    def get_sensor(self, sensor: Union[PlantSensor, Sensor]):

        with Session(self.engine) as session:
            if isinstance(sensor, Sensor):
                statement = select(Sensor).where(Sensor.serial_number == sensor.serial_number)
                sensor = session.exec(statement).first()
            elif isinstance(sensor, PlantSensor):
                statement = select(PlantSensor).where(PlantSensor.serial_number == sensor.serial_number)
                sensor = session.exec(statement).first()

        return sensor
    
    def add_data_entry(self, sensor_entry: Union[PlantSensorEntry, HumityTemperatureEntry]):

        with Session(self.engine) as session:
            try:
                session.add(sensor_entry)
            except Exception as e:
                session.rollback()
                logger.error('could save the sensor entry in the database')
                logger.error(e)
            else:
                session.commit()
                session.refresh(sensor_entry)
                

        return sensor_entry
    