from sqlmodel import create_engine, Session
from .models import *
from .abstract_repository import AbstractRepository

logger = logging.getLogger(__name__)


class SQLModel_repository(AbstractRepository):

    def __init__(self, engine):
        self.engine = engine
    
    def add_room(self,room: Room):
        #TODO: handle the case where data is not succesfully saved, should return and error
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