from sqlmodel import create_engine, Session, select, func
from sqlalchemy.orm import joinedload

from src.models import Room
from .models import *
from .abstract_repository import AbstractRepository

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
        
    def get_room(self, room: Room):

        with Session(self.engine) as session:
            statement = select(Room).where(func.lower(Room.name) == room.name.lower())
            room = session.exec(statement).first()
        return room

    def add_sensor(self, sensor: Sensor):

        with Session(self.engine) as session:
            try:
                session.add(sensor)
            except Exception as e:
                session.rollback()
                logger.error('could not insert new room in database')
                logger.error(e)
            else:
                session.commit()
                session.refresh(sensor)

        return sensor