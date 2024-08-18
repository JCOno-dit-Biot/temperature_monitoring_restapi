from src.models import *
from src.orm import *
from typing import Union
import logging
from datetime import datetime, timezone

def parse_measurement_dict(data_dict):
        
        try:
            entry_timestamp =  datetime.fromtimestamp(int(data_dict["timestamp"]), tz = timezone.utc)
        except KeyError as e:
            entry_timestamp = datetime.now(timezone.utc)
            data_dict["timestamp"] = entry_timestamp
            logging.warning(e)
            logging.warning("could not parse timestamp to utc time, using now as the measurement time")

        measurement_validation = Measurement(**data_dict)

        measurement_obj = create_db_sensor_entry_from_measurement(measurement_validation)

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
    