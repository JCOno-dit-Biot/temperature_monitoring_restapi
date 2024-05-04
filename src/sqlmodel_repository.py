from sqlmodel import create_engine, Session, select, func
from sqlalchemy.orm import joinedload, join
from .models import *
from .abstract_repository import AbstractRepository
from typing import Union
from sqlalchemy.exc import IntegrityError, OperationalError, DataError, ProgrammingError


logger = logging.getLogger(__name__)


class SQLModel_repository(AbstractRepository):

    def __init__(self, engine):
        self.engine = engine
    
    def add_room(self,room: Room):
        with Session(self.engine) as session:
            
            #Convert the value to lowercase and check if it already exists
            #TODO: use get_room instead
            exists = session.exec(select(Room).where(func.lower(Room.name) == room.name.lower())).first()
            
            if exists:
                session.rollback()
                raise ValueError("Entry with this value already exists.")
            
            else:
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

            
        
    def add_plant(self, plant):
        '''
        Add a new plant in the database, plant name is unique.
        This method can only be called when adding a sensor to the database currently
        '''
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
        '''
        Method to check if a room exists in the database
        '''
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

        ''' Get sensor, depending on the class of sensor it will find the plant or regular sensor'''

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
    
    #as a first step the average temperature collects only from regular sensors
    def get_average_temperature(self, room = None):
        average_temperature = None

        with Session(self.engine) as session:
            query = select(func.avg(HumityTemperatureEntry.temperature)).join(Sensor, HumityTemperatureEntry.sensor_id == Sensor.serial_number)

            if room is not None:
                query =  query.where(Sensor.room == room)

            try:
                average_temperature = session.scalar(query)
            
            except Exception as e:
                logger.error("could not calculate average temperature")
                logger.error(e)

        return average_temperature