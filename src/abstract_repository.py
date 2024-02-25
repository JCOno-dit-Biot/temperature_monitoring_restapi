import abc
from .models import *
from typing import Union

class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_room(self, room: Room):
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_room(self, room: Room):
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_sensor(self, sensor: Sensor):
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_sensor(self, sensor: Union[Sensor, PlantSensor]):
        raise NotImplementedError

    @abc.abstractmethod
    def add_data_entry(self, sensor_entry: Union[PlantSensorEntry, HumityTemperatureEntry]):
        raise NotImplementedError

    # def add_measurement(self, measurement: measurement, room_id: int):
    #     raise NotImplementedError
    
    # def get_number_days_monitoring(self):
    #     raise NotImplementedError