from .models import *
import abc
import logging

logger = logging.getLogger(__name__)

class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_room(self, room: room):
        raise NotImplementedError
    
    def add_measurement(self, measurement: measurement, room_id: int):
        raise NotImplementedError
    
    def get_number_days_monitoring(self):
        raise NotImplementedError
    

class PostgreSQLRepository(AbstractRepository):

    def __init__(self, connection):
        self.connection = connection

    def add_room(self, room: room):

        with self.connection.cursor() as cur:
            try:
                cur.execute('INSERT INTO rooms (name) VALUES (%s) RETURNING id;', (room.name,))
                room_id = cur.fetchone()[0]
            except Exception as e:
                self.connection.rollback()
                logger.error('could not insert new room in database')
                logger.error(e)
            else:
                self.connection.commit()
        
        return room_id
    
    def get_room_id(self, room: room):
        with self.connection.cursor() as cur:
            room_id = None
            try:
                cur.execute('SELECT id FROM rooms WHERE name = (%s)',(room.name,))
                room_id = cur.fetchone()[0]
            except Exception as e:
                logger.error(f'could not find room {room.name} in database')
                logger.error(e)

            return room_id


    def add_measurement(self, measurement: measurement, room_id):
        

         with self.connection.cursor() as cur:
            try:
                cur.execute('INSERT INTO sensor_entry (room_id, entry_timestamp, temperature, humidity) \
                            VALUES (%s, %s, %s, %s)', (room_id, measurement.entry_timestamp, measurement.temperature, measurement.humidity,))
            except Exception as e:
                self.connection.rollback()
                logger.error('could not insert new meaasurement in database')
                logger.error(e)
            else:
                self.connection.commit()
    
    def get_average_average_temperature(self, room = None):
        
        with self.connection.cursor() as cur:
            try:
                if room is not None:
                    cur.execute("SELECT AVG(temperature) AS avg_temperature FROM sensor_entry WHERE room_id = (SELECT id FROM rooms WHERE name = %s)", (room.name))
                    total_number_days = cur.fetchone()
                else:
                    cur.execute("SELECT AVG(temperature) AS avg_temperature FROM sensor_entry")
                    total_number_days = cur.fetchone()
            except Exception as e:
                logger.error("could not calculate average temperature")
                logger.error(e)

        return total_number_days
    
    def get_number_days_monitoring(self):
        
        with self.connection.cursor() as cur:
            try:
                cur.execute("SELECT COUNT (*) AS DAYS FROM sensor_entry")
                total_number_days = cur.fetchone()
            except Exception as e:
                logger.error(e)

        return total_number_days

