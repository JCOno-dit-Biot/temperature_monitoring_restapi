import abc
from .models import *

class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_room(self, room: Room):
        raise NotImplementedError
    
    # def add_measurement(self, measurement: measurement, room_id: int):
    #     raise NotImplementedError
    
    # def get_number_days_monitoring(self):
    #     raise NotImplementedError