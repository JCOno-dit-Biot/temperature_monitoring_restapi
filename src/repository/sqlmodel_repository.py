from sqlmodel import create_engine, Session, select, func
from sqlalchemy.orm import joinedload, join
from ..orm import *
import logging
from .abstract_repository import AbstractRepository
from typing import Union
from sqlalchemy.exc import IntegrityError, OperationalError, DataError, ProgrammingError


logger = logging.getLogger(__name__)


class SQLModel_repository(AbstractRepository):

    def __init__(self, engine):
        self.engine = engine
    
    
    def get_room(self, room: Room):
        '''
        Method to check if a room exists in the database
        '''

        with Session(self.engine) as session:
            #this method is case insensitive
            if isinstance(room.name, str):
                statement = select(Room).where(func.lower(Room.name) == room.name.lower())
                room = session.exec(statement).first()
            else: 
                room = None
        return room
    
    #Validation is not performed by pydantic when the SQLmodel as Table set to True, so this method
    #makes sure the room name is a string
    def add_room(self,room: Room):
        '''
        Add a room to the database table is it does not exist
        This method is not case sensitive (if Living-Room is saved in the database, 
        living-room would not be save)
        '''

        with Session(self.engine) as session:
            
            #Check if room is already in database (not case sensitive)
            exists = self.get_room(room)
            
            if exists:
                session.rollback()
                raise ValueError(f"Room with name {room.name} already exists.")
            
            else:
                #Validation is not performed by pydantic when the SQLmodel as Table set to True, so this method
                #makes sure the room name is a string
                if isinstance(room.name, str):
                    try:
                        session.add(room)
                        
                    except Exception as e:
                        session.rollback()
                        logger.error('could not insert new room in database')
                        raise Exception
                    else:
                        session.commit()
                        session.refresh(room)
                        return room
                else:
                    raise TypeError('Room name must be a string')

            
        
    def add_plant(self, plant):
        '''
        Add a new plant in the database, plant name is unique.
        This method is only be called when adding a plant sensor to the database currently
        '''
        if isinstance(plant.name, str):
            plant.name = plant.name.lower()

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

        
    def get_plant(self, plant: Plant):
        '''
        Method to check if a plant already exists in the database (not case sensitive)
        '''
        with Session(self.engine) as session:
            if isinstance(plant.name, str):
                statement = select(Plant).where(func.lower(Plant.name) == plant.name.lower())
                plant = session.exec(statement).first()
            else:
                plant = None
        return plant
    
    def add_sensor(self, sensor: Union[Sensor, PlantSensor]):
        '''
        Add sensor to the database, depending on the class that is passed in, 
        it will save a plant or regular sensor
        '''
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
        ''' 
        Get sensor, depending on the class of sensor it will find the plant or regular sensor
        '''
        with Session(self.engine) as session:
            if isinstance(sensor, Sensor):
                statement = select(Sensor).where(Sensor.serial_number == sensor.serial_number)
                sensor = session.exec(statement).first()
            elif isinstance(sensor, PlantSensor):
                statement = select(PlantSensor).where(PlantSensor.serial_number == sensor.serial_number)
                sensor = session.exec(statement).first()

        return sensor
    
    #rework this method to take the pydantic measurement class and interact with the write table
    def add_data_entry(self, sensor_entry: Union[PlantSensorEntry, HumidityTemperatureEntry]):
        '''
        Add measurements to the database, depending on the type of data,
        it will be added to the relevent table
        '''
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
    
   
    def get_average_temperature(self, room : Optional[Room] = None):
        '''
        This method calculates the average temperature of a room
        For now it only considers temperature from regular sensor
        '''

        average_temperature = None

        with Session(self.engine) as session:
            query = select(func.avg(HumidityTemperatureEntry.temperature)).join(Sensor, HumidityTemperatureEntry.sensor_id == Sensor.serial_number)

            if room is not None:
                query =  query.where(Sensor.room == room)

            try:
                average_temperature = session.scalar(query)
            
            except Exception as e:
                logger.error("could not calculate average temperature")
                logger.error(e)

        return average_temperature