from src.models import *
from src.orm import *
from typing import Union
import logging
from datetime import datetime, timezone
import pytz

def parse_measurement(measurement):
        
        if measurement.entry_timestamp is not None:
            try:
                #check if datetime and what timezone
                entry_timestamp =  datetime.fromtimestamp(measurement.entry_timestamp, tz = timezone.utc)
            except TypeError as e:
                if isinstance(measurement.entry_timestamp, datetime) and measurement.entry_timestamp.tzinfo is None:
                    logging.warning("timestamp was already in a datetime format instead of the expected epoch timestamp")
                    measurement.entry_timestamp = pytz.utc.localize(measurement.entry_timestamp)
                    
        else:
            measurement.entry_timestamp = datetime.now(timezone.utc)
            logging.warning("could not parse timestamp to utc time, using now as the measurement time")


        measurement_obj = create_db_sensor_entry_from_measurement(measurement)

        return measurement_obj


def create_db_sensor_entry_from_measurement(measurement: Measurement) -> Union[PlantSensorEntry, HumidityTemperatureEntry]:

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
        db_sensor_entry = HumidityTemperatureEntry(
            sensor_id = measurement.sensor_id,
            entry_timestamp = measurement.entry_timestamp,
            temperature = measurement.temperature,
            humidity = measurement.humidity
        )

    return db_sensor_entry
    