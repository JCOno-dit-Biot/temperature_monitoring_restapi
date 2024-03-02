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
    def add_plant(self, plant):
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_sensor(self, sensor: Sensor):
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_sensor(self, sensor: Union[Sensor, PlantSensor]):
        raise NotImplementedError

    @abc.abstractmethod
    def get_plant(self, plant: Plant):
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_data_entry(self, sensor_entry: Union[PlantSensorEntry, HumityTemperatureEntry]):
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_average_temperature(avg_room):
        raise NotImplementedError
    
    # def get_number_days_monitoring(self):
    #     raise NotImplementedError