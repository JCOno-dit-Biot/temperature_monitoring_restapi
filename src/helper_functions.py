from src.models import *
from src.orm import *
from typing import Union


def create_db_sensor_entry_from_measurement(measurement: Measurement) -> Union[PlantSensorEntry, HumityTemperatureEntry]:

    db_sensor_entry = None
    #only plant sensors report wetness, the default wetness (if not provided) is None. 
    if measurement.wetness is not None:
        db_sensor_entry = PlantSensorEntry(
            sensor_id = measurement.sensor_id,
            entry_timestamp = measurement.entry_timestamp,
            temperature = measurement.temperature,
            humidity = measurement.humidity,
            wetness = measurement.wetness
        )
    else:
        db_sensor_entry = HumityTemperatureEntry(
            sensor_id = measurement.sensor_id,
            entry_timestamp = measurement.entry_timestamp,
            temperature = measurement.temperature,
            humidity = measurement.humidity
        )

    return db_sensor_entry
    